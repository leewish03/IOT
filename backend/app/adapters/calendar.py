from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from ..schemas.models import CalendarEvent


class CalendarAdapter(ABC):
    @abstractmethod
    def get_tomorrow(self, timezone: str = "Asia/Seoul") -> list[CalendarEvent]:
        raise NotImplementedError


class FileCalendarAdapter(CalendarAdapter):
    def __init__(self, calendar_file: Path) -> None:
        self.calendar_file = calendar_file

    def get_tomorrow(self, timezone: str = "Asia/Seoul") -> list[CalendarEvent]:
        if not self.calendar_file.exists():
            return []
        raw = json.loads(self.calendar_file.read_text(encoding="utf-8"))
        events = [self._event_from_dict(item) for item in raw.get("events", [])]
        tz = ZoneInfo(timezone)
        tomorrow = datetime.now(tz).date() + timedelta(days=1)
        return [event for event in events if self._event_date(event.start, tz) == tomorrow]

    @staticmethod
    def _event_from_dict(item: dict[str, Any]) -> CalendarEvent:
        return CalendarEvent(
            event_id=str(item["event_id"]),
            title=str(item["title"]),
            start=str(item["start"]),
            end=item.get("end"),
            must_wake=bool(item.get("must_wake", False)),
            source=str(item.get("source", "file")),
        )

    @staticmethod
    def _event_date(value: str, timezone: ZoneInfo):
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone)
        return parsed.astimezone(timezone).date()


class NaverCalendarReadAdapter(CalendarAdapter):
    def get_tomorrow(self, timezone: str = "Asia/Seoul") -> list[CalendarEvent]:
        raise NotImplementedError(
            "NAVER's public Calendar Open API is documented for schedule creation. "
            "Use Google Calendar or a file adapter for MVP read access unless a maintainable "
            "Naver read source is confirmed."
        )


class GoogleCalendarAdapter(CalendarAdapter):
    def get_tomorrow(self, timezone: str = "Asia/Seoul") -> list[CalendarEvent]:
        raise NotImplementedError(
            "Google Calendar read access requires credentials. Implement this adapter after "
            "GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CALENDAR_ID are available."
        )
