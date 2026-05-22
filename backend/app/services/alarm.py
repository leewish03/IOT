from __future__ import annotations

import uuid
from datetime import UTC, datetime

from ..adapters.home_assistant import HomeAssistantClient
from ..schemas.models import Alarm, utcnow_iso
from ..store import InMemoryStore
from .policies import PolicyRegistry


class AlarmService:
    def __init__(
        self,
        store: InMemoryStore,
        home_assistant: HomeAssistantClient,
        policies: PolicyRegistry,
    ) -> None:
        self.store = store
        self.home_assistant = home_assistant
        self.policies = policies

    def create(self, time: str, profile: str, label: str, linked_event_id: str | None = None) -> Alarm:
        _parse_alarm_time(time)
        self._validate_profile(profile)
        alarm = Alarm(
            alarm_id=str(uuid.uuid4()),
            time=time,
            profile=profile,
            label=label,
            linked_event_id=linked_event_id,
        )
        self.store.alarms[alarm.alarm_id] = alarm
        self.home_assistant.run_alarm(
            {
                "alarm_id": alarm.alarm_id,
                "time": time,
                "profile": profile,
                "label": label,
                "linked_event_id": linked_event_id,
            }
        )
        return alarm

    def update_profile(self, alarm_id: str, profile: str) -> Alarm:
        self._validate_profile(profile)
        if alarm_id not in self.store.alarms:
            raise ValueError(f"Unknown alarm_id: {alarm_id}")
        alarm = self.store.alarms[alarm_id]
        alarm.profile = profile
        alarm.updated_at = utcnow_iso()
        return alarm

    def next_alarm(self) -> Alarm | None:
        now = datetime.now(UTC)
        enabled = [
            alarm
            for alarm in self.store.alarms.values()
            if alarm.enabled and _parse_alarm_time(alarm.time) >= now
        ]
        return sorted(enabled, key=lambda alarm: _parse_alarm_time(alarm.time))[0] if enabled else None

    def _validate_profile(self, profile: str) -> None:
        profile_ids = self.policies.profile_ids()
        if profile_ids and profile not in profile_ids:
            raise ValueError(f"Unknown alarm profile: {profile}")


def _parse_alarm_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
