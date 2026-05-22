from __future__ import annotations

from abc import ABC, abstractmethod
from ..schemas.models import RelayState, utcnow_iso
from ..store import InMemoryStore


VALID_CHANNELS = {"ch1", "ch2"}
VALID_ACTIONS = {"on", "off"}


class RelayAdapter(ABC):
    @abstractmethod
    def get_state(self, device_id: str) -> RelayState:
        raise NotImplementedError

    @abstractmethod
    def set_channel(self, device_id: str, channel: str, action: str) -> RelayState:
        raise NotImplementedError


class InMemoryRelayAdapter(RelayAdapter):
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def get_state(self, device_id: str) -> RelayState:
        return self._get_or_create(device_id)

    def set_channel(self, device_id: str, channel: str, action: str) -> RelayState:
        if channel not in VALID_CHANNELS:
            raise ValueError(f"Invalid relay channel: {channel}")
        if action not in VALID_ACTIONS:
            raise ValueError(f"Invalid relay action: {action}")

        state = self._get_or_create(device_id)
        state.channels[channel] = action == "on"
        state.online = True
        state.last_seen = utcnow_iso()
        state.last_command_result = f"{channel}:{action}"
        return state

    def report_state(
        self,
        device_id: str,
        channels: dict[str, bool],
        firmware: str | None = None,
        rssi: int | None = None,
    ) -> RelayState:
        unknown = set(channels) - VALID_CHANNELS
        if unknown:
            raise ValueError(f"Invalid relay channel(s): {', '.join(sorted(unknown))}")
        state = self._get_or_create(device_id)
        state.channels.update(channels)
        state.online = True
        state.last_seen = utcnow_iso()
        if firmware:
            state.firmware = firmware
        if rssi is not None:
            state.rssi = rssi
        return state

    def _get_or_create(self, device_id: str) -> RelayState:
        if device_id not in self.store.relays:
            self.store.relays[device_id] = RelayState(device_id=device_id)
        return self.store.relays[device_id]
