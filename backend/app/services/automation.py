from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from ..adapters.calendar import CalendarAdapter
from ..schemas.models import CalendarEvent, to_jsonable
from .alarm import AlarmService


class AutomationService:
    """MVP automation runner for YAML rules under policies/automation_rules/."""

    def __init__(self, calendar: CalendarAdapter, alarm: AlarmService, timezone: str) -> None:
        self.calendar = calendar
        self.alarm = alarm
        self.timezone = timezone

    def prepare_class_day(self, profile: str = "aggressive", offset_min: int = 30) -> dict[str, Any]:
        """Apply class_day_wakeup: alarm for first must_wake event tomorrow, offset before start."""
        events = self.calendar.get_tomorrow(self.timezone)
        candidates = [event for event in events if event.must_wake]
        if not candidates:
            return {"prepared": False, "reason": "no_must_wake_events_tomorrow", "events_checked": len(events)}

        event = sorted(candidates, key=lambda item: item.start)[0]
        alarm_time = _offset_iso(event.start, self.timezone, offset_min)
        alarm = self.alarm.create(
            time=alarm_time,
            profile=profile,
            label=f"class_day:{event.title}",
            linked_event_id=event.event_id,
        )
        return {
            "prepared": True,
            "rule_id": "class_day_wakeup",
            "event": to_jsonable(event),
            "alarm": to_jsonable(alarm),
            "offset_min": offset_min,
        }


def _offset_iso(start: str, timezone: str, offset_min: int) -> str:
    tz = ZoneInfo(timezone)
    normalized = start.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    wake_at = parsed.astimezone(tz) - timedelta(minutes=offset_min)
    return wake_at.replace(microsecond=0).isoformat()
