from __future__ import annotations

from dataclasses import dataclass, field

from .schemas.models import Alarm, EnvironmentSnapshot, RelayState, ScheduleJob


@dataclass
class InMemoryStore:
    default_device_id: str
    relays: dict[str, RelayState] = field(default_factory=dict)
    schedules: dict[str, ScheduleJob] = field(default_factory=dict)
    alarms: dict[str, Alarm] = field(default_factory=dict)
    environment: EnvironmentSnapshot = field(
        default_factory=lambda: EnvironmentSnapshot(temperature_c=22.5, humidity_pct=48.0)
    )

    def __post_init__(self) -> None:
        if self.default_device_id not in self.relays:
            self.relays[self.default_device_id] = RelayState(device_id=self.default_device_id)
