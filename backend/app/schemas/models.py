from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import UTC, datetime
from typing import Any


ChannelName = str


def utcnow_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {k: to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    return value


@dataclass
class RelayState:
    device_id: str
    channels: dict[ChannelName, bool] = field(default_factory=lambda: {"ch1": False, "ch2": False})
    online: bool = True
    last_seen: str = field(default_factory=utcnow_iso)
    firmware: str = "mock-0.1.0"
    rssi: int | None = None
    last_command_result: str | None = None


@dataclass
class ScheduleJob:
    job_id: str
    device_id: str
    channel: ChannelName
    action: str
    execute_at: str
    status: str = "pending"
    created_at: str = field(default_factory=utcnow_iso)
    executed_at: str | None = None


@dataclass
class CalendarEvent:
    event_id: str
    title: str
    start: str
    end: str | None = None
    must_wake: bool = False
    source: str = "file"


@dataclass
class Alarm:
    alarm_id: str
    time: str
    profile: str
    label: str
    linked_event_id: str | None = None
    enabled: bool = True
    created_at: str = field(default_factory=utcnow_iso)
    updated_at: str | None = None


@dataclass
class AuditEvent:
    event_id: str
    actor: str
    source: str
    tool_name: str
    validated_input: dict[str, Any]
    result: dict[str, Any]
    timestamp: str
    correlation_id: str


@dataclass
class EnvironmentSnapshot:
    temperature_c: float
    humidity_pct: float
    updated_at: str = field(default_factory=utcnow_iso)
    source: str = "mock"


@dataclass
class ToolResult:
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {"success": self.success, "data": to_jsonable(self.data)}
        if self.error:
            payload["error"] = self.error
        return payload
