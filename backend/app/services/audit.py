from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from ..schemas.models import AuditEvent, utcnow_iso


class AuditLog:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        *,
        actor: str,
        source: str,
        tool_name: str,
        validated_input: dict[str, Any],
        result: dict[str, Any],
        correlation_id: str | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            actor=actor,
            source=source,
            tool_name=tool_name,
            validated_input=validated_input,
            result=result,
            timestamp=utcnow_iso(),
            correlation_id=correlation_id or str(uuid.uuid4()),
        )
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.__dict__, ensure_ascii=False) + "\n")
        return event

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.log_path.exists():
            return []
        lines = self.log_path.read_text(encoding="utf-8").splitlines()
        selected = lines[-limit:]
        return [json.loads(line) for line in selected if line.strip()]
