from __future__ import annotations

from dataclasses import dataclass, field

from .schemas.models import Alarm, RelayState, ScheduleJob


@dataclass
class InMemoryStore:
    default_device_id: str
    relays: dict[str, RelayState] = field(default_factory=dict)
    schedules: dict[str, ScheduleJob] = field(default_factory=dict)
    alarms: dict[str, Alarm] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.default_device_id not in self.relays:
            self.relays[self.default_device_id] = RelayState(device_id=self.default_device_id)
