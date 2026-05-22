from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HomeAssistantClient:
    base_url: str
    token: str
    alarm_service: str
    dry_run: bool = True

    def call_service(self, service_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.dry_run:
            return {
                "called": False,
                "dry_run": True,
                "service": service_name,
                "payload": payload,
            }

        try:
            import httpx  # type: ignore
        except ImportError as exc:
            raise RuntimeError("httpx is required for live Home Assistant calls") from exc

        domain, service = service_name.split(".", 1)
        url = f"{self.base_url.rstrip('/')}/api/services/{domain}/{service}"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        response = httpx.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return {"called": True, "dry_run": False, "service": service_name, "response": response.json()}

    def run_alarm(self, alarm_payload: dict[str, Any]) -> dict[str, Any]:
        return self.call_service(self.alarm_service, alarm_payload)
