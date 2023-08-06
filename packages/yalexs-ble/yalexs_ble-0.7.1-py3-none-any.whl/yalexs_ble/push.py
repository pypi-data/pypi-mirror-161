from __future__ import annotations

import asyncio
import logging
import struct
from collections.abc import Callable
from typing import Any, TypeVar, cast

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak_retry_connector import BleakError

from .const import (
    APPLE_MFR_ID,
    HAP_FIRST_BYTE,
    YALE_MFR_ID,
    DoorStatus,
    LockState,
    LockStatus,
)
from .lock import Lock
from .session import AuthError, DisconnectedError, ResponseError

_LOGGER = logging.getLogger(__name__)


WrapFuncType = TypeVar("WrapFuncType", bound=Callable[..., Any])

DEFAULT_ATTEMPTS = 3

ADV_UPDATE_COALESCE_SECONDS = 10

HK_UPDATE_COALESCE_SECONDS = 1

UPDATE_IN_PROGRESS_DEFER_SECONDS = 60


def operation_lock(func: WrapFuncType) -> WrapFuncType:
    """Define a wrapper to only allow a single operation at a time."""

    async def _async_wrap_operation_lock(
        self: "PushLock", *args: Any, **kwargs: Any
    ) -> None:
        _LOGGER.debug("%s: Acquiring lock", self.name)
        async with self._operation_lock:
            return await func(self, *args, **kwargs)

    return cast(WrapFuncType, _async_wrap_operation_lock)


def retry_bluetooth_connection_error(func: WrapFuncType) -> WrapFuncType:
    """Define a wrapper to retry on bleak error.

    The accessory is allowed to disconnect us any time so
    we need to retry the operation.
    """

    async def _async_wrap_retry_bluetooth_connection_error(
        self: "PushLock", *args: Any, **kwargs: Any
    ) -> Any:
        _LOGGER.debug("%s: Starting retry loop", self.name)
        attempts = DEFAULT_ATTEMPTS
        max_attempts = attempts - 1

        for attempt in range(attempts):
            try:
                return await func(self, *args, **kwargs)
            except (
                asyncio.TimeoutError,
                ResponseError,
                DisconnectedError,
                BleakError,
                EOFError,
            ) as err:
                if attempt == max_attempts:
                    raise
                _LOGGER.debug(
                    "%s: %s error calling %s, retrying...",
                    self.name,
                    type(err),
                    func,
                    exc_info=True,
                )
            except AuthError:
                raise

    return cast(WrapFuncType, _async_wrap_retry_bluetooth_connection_error)


class PushLock:
    """A lock with push updates."""

    def __init__(self, local_name: str) -> None:
        """Init the lock watcher."""
        self._local_name = local_name
        self._lock_state: LockState | None = None
        self._last_adv_value = -1
        self._last_hk_state = -1
        self._lock_key: str | None = None
        self._lock_key_index: int | None = None
        self._ble_device: BLEDevice | None = None
        self._operation_lock = asyncio.Lock()
        self._running = False
        self._callbacks: list[Callable[[LockState], None]] = []
        self._update_task: asyncio.Task | None = None  # type: ignore[type-arg]
        self._debounce_lock = asyncio.Lock()
        self.loop = asyncio._get_running_loop()
        self._cancel_deferred_update: asyncio.TimerHandle | None = None

    @property
    def local_name(self) -> str:
        """Get the local name."""
        return self._local_name

    @property
    def name(self) -> str:
        """Get the name of the lock."""
        return self._local_name

    @property
    def door_status(self) -> DoorStatus:
        """Return the current door status."""
        return self._lock_state.door if self._lock_state else DoorStatus.UNKNOWN

    @property
    def lock_status(self) -> LockStatus:
        """Return the current lock status."""
        return self._lock_state.lock if self._lock_state else LockStatus.UNKNOWN

    @property
    def lock_state(self) -> LockState | None:
        """Return the current lock state."""
        return self._lock_state

    def register_callback(
        self, callback: Callable[[LockState], None]
    ) -> Callable[[], None]:
        """Register a callback to be called when the lock state changes."""

        def unregister_callback() -> None:
            self._callbacks.remove(callback)

        self._callbacks.append(callback)
        return unregister_callback

    def set_lock_key(self, key: str, slot: int) -> None:
        """Set the lock key."""
        self._lock_key = key
        self._lock_key_index = slot

    def set_ble_device(self, ble_device: BLEDevice) -> None:
        """Set the ble device."""
        self._ble_device = ble_device

    def _get_lock_instance(self) -> Lock:
        """Get the lock instance."""
        assert self._ble_device is not None  # nosec
        assert self._lock_key is not None  # nosec
        assert self._lock_key_index is not None  # nosec
        return Lock(self._ble_device, self._lock_key, self._lock_key_index)

    async def _cancel_any_update(self) -> None:
        """Cancel any update task."""
        await asyncio.sleep(0)
        self._cancel_in_progress_update()

    def _cancel_in_progress_update(self) -> None:
        """Cancel any in progress update task."""
        if self._update_task:
            _LOGGER.debug("Canceling in progress update: %s", self._update_task)
            self._update_task.cancel()
            self._update_task = None

    @operation_lock
    @retry_bluetooth_connection_error
    async def lock(self) -> None:
        """Lock the lock."""
        _LOGGER.debug("Starting lock")
        await self._cancel_any_update()
        self._callback_state(LockState(LockStatus.LOCKING, self.door_status))
        lock = self._get_lock_instance()
        try:
            await lock.connect()
            await lock.force_lock()
        except Exception:
            self._callback_state(LockState(LockStatus.UNKNOWN, self.door_status))
            raise
        finally:
            await lock.disconnect()
        self._callback_state(LockState(LockStatus.LOCKED, self.door_status))
        await self._cancel_any_update()
        _LOGGER.debug("Finished lock")

    @operation_lock
    @retry_bluetooth_connection_error
    async def unlock(self) -> None:
        """Unlock the lock."""
        _LOGGER.debug("Starting unlock")
        await self._cancel_any_update()
        self._callback_state(LockState(LockStatus.UNLOCKING, self.door_status))
        lock = self._get_lock_instance()
        try:
            await lock.connect()
            await lock.force_unlock()
        except Exception:
            self._callback_state(LockState(LockStatus.UNKNOWN, self.door_status))
            raise
        finally:
            await lock.disconnect()
        self._callback_state(LockState(LockStatus.UNLOCKED, self.door_status))
        await self._cancel_any_update()
        _LOGGER.debug("Finished unlock")

    @operation_lock
    @retry_bluetooth_connection_error
    async def update(self) -> LockState:
        """Update the lock state."""
        lock = self._get_lock_instance()
        try:
            await lock.connect()
            state = await lock.status()
        except asyncio.CancelledError:
            _LOGGER.debug(
                "%s: In-progress update canceled due to lock operation", self.name
            )
            raise
        finally:
            await lock.disconnect()
        _LOGGER.debug("%s: Updating lock state", self.name)
        self._callback_state(state)
        return state

    def _callback_state(self, lock_state: LockState) -> None:
        """Call the callbacks."""
        self._lock_state = lock_state
        _LOGGER.debug("%s: New lock state: %s", self.name, self._lock_state)
        for callback in self._callbacks:
            try:
                callback(lock_state)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("%s: Error calling callback", self.name)

    def update_advertisement(
        self, ble_device: BLEDevice, ad: AdvertisementData
    ) -> None:
        """Update the advertisement."""
        if ble_device.name != self._local_name:
            return
        _LOGGER.debug(
            "%s: Accepting new advertisement since local name does match: %s: %s",
            self.name,
            ble_device.name,
            ad,
        )
        self.set_ble_device(ble_device)
        has_update = 0
        mfr_data = dict(ad.manufacturer_data)
        if APPLE_MFR_ID in mfr_data and mfr_data[APPLE_MFR_ID][0] == HAP_FIRST_BYTE:
            hk_state = get_homekit_state_num(mfr_data[APPLE_MFR_ID])
            # Sometimes the yale data is glued on to the end of the HomeKit data
            # but in that case it seems wrong so we don't process it
            #
            # if len(mfr_data[APPLE_MFR_ID]) > 20 and YALE_MFR_ID not in mfr_data:
            # mfr_data[YALE_MFR_ID] = mfr_data[APPLE_MFR_ID][20:]
            if hk_state != self._last_hk_state:
                has_update = HK_UPDATE_COALESCE_SECONDS
                self._last_hk_state = hk_state
        if YALE_MFR_ID in mfr_data:
            current_value = mfr_data[YALE_MFR_ID][0]
            if current_value != self._last_adv_value:
                has_update = ADV_UPDATE_COALESCE_SECONDS
                self._last_adv_value = current_value
        _LOGGER.debug(
            "%s: State: (current_state: %s) (hk_state: %s) "
            "(adv_value: %s) (has_update: %s)",
            self.name,
            self._lock_state,
            self._last_hk_state,
            self._last_adv_value,
            has_update,
        )
        if has_update:
            self._schedule_update(has_update)

    async def start(self) -> Callable[[], None]:
        """Start watching for updates."""
        _LOGGER.debug("Waiting for advertisement callbacks for %s", self.name)
        if self._running:
            raise RuntimeError("Already running")
        self._running = True

        def _cancel() -> None:
            self._running = False
            self._cancel_in_progress_update()

        return _cancel

    def _schedule_update(self, seconds: float) -> None:
        """Schedule an update."""
        now = self.loop.time()
        future_update_time = seconds
        if self._cancel_deferred_update:
            time_till_update = self._cancel_deferred_update.when() - now
            if future_update_time < HK_UPDATE_COALESCE_SECONDS:
                future_update_time = HK_UPDATE_COALESCE_SECONDS
                _LOGGER.debug(
                    "%s: Existing update too soon %s, "
                    "rescheduling update for in %s seconds",
                    self.name,
                    time_till_update,
                    future_update_time,
                )
            elif time_till_update < seconds:
                _LOGGER.debug(
                    "%s: Existing update in %s seconds will happen sooner than now",
                    self.name,
                    time_till_update,
                )
                return
            _LOGGER.debug("%s: Rescheduling update", self.name)
            self._cancel_deferred_update.cancel()
            self._cancel_deferred_update = None
        _LOGGER.debug(
            "%s: Scheduling update to happen in %s seconds",
            self.name,
            future_update_time,
        )
        self._cancel_deferred_update = self.loop.call_at(
            now + future_update_time, self._deferred_update
        )

    def _deferred_update(self) -> None:
        """Update the lock state."""
        if self._debounce_lock.locked():
            _LOGGER.debug(
                "%s: Rescheduling update since one already in progress", self.name
            )
            self._schedule_update(UPDATE_IN_PROGRESS_DEFER_SECONDS)
            return
        self._cancel_deferred_update = None
        self.loop.create_task(self.update())

    async def _queue_update(self) -> None:
        """Watch for updates."""
        async with self._debounce_lock:
            if not self._running:
                return
            _LOGGER.debug("%s: Starting update", self.name)
            try:
                self._update_task = asyncio.create_task(self.update())
                await self._update_task
            except AuthError as ex:
                _LOGGER.error(
                    "%s: Auth error, key or slot (key index) is incorrect: %s",
                    self.name,
                    ex,
                    exc_info=True,
                )
            except asyncio.CancelledError:
                _LOGGER.debug("%s: In-progress update canceled", self.name)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("%s: Error updating", self.name)


def get_homekit_state_num(data: bytes) -> int:
    """Get the homekit state number from the manufacturer data."""
    acid, gsn, cn, cv = struct.unpack("<HHBB", data[9:15])
    return gsn
