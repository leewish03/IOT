from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Callable, Any

from ..adapters.relay import RelayAdapter
from ..adapters.relay import VALID_ACTIONS, VALID_CHANNELS
from ..schemas.models import ScheduleJob
from ..store import InMemoryStore


class SchedulerService:
    def __init__(self, store: InMemoryStore, relay_adapter: RelayAdapter) -> None:
        self.store = store
        self.relay_adapter = relay_adapter
        self.command_executor: Callable[[ScheduleJob], dict[str, Any]] | None = None

    def create_relay_schedule(self, device_id: str, channel: str, action: str, execute_at: str) -> ScheduleJob:
        if channel not in VALID_CHANNELS:
            raise ValueError(f"Invalid relay channel: {channel}")
        if action not in VALID_ACTIONS:
            raise ValueError(f"Invalid relay action: {action}")
        _parse_iso(execute_at)
        job = ScheduleJob(
            job_id=str(uuid.uuid4()),
            device_id=device_id,
            channel=channel,
            action=action,
            execute_at=execute_at,
        )
        self.store.schedules[job.job_id] = job
        return job

    def execute_due(self, now_iso: str | None = None) -> list[ScheduleJob]:
        now = _parse_iso(now_iso) if now_iso else datetime.now(UTC)
        executed: list[ScheduleJob] = []
        for job in self.store.schedules.values():
            if job.status != "pending":
                continue
            if _parse_iso(job.execute_at) <= now:
                if self.command_executor:
                    self.command_executor(job)
                else:
                    self.relay_adapter.set_channel(job.device_id, job.channel, job.action)
                job.status = "executed"
                job.executed_at = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
                executed.append(job)
        return executed


def _parse_iso(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
