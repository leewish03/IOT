from __future__ import annotations

from typing import Any

from ..services.orchestrator import Orchestrator
from ..services.validation import TOOL_SCHEMAS


class McpCatalogServer:
    """MCP-style contract surface.

    This class intentionally keeps the contract independent from a specific Python MCP SDK so
    Open WebUI integration can use the same Resource/Tool/Prompt definitions once the deployment
    environment chooses its MCP transport.
    """

    RESOURCES = [
        {"uri": "home://devices/relay", "name": "Relay devices"},
        {"uri": "home://calendar/tomorrow", "name": "Tomorrow calendar"},
        {"uri": "home://alarm/next", "name": "Next alarm"},
        {"uri": "home://automation/active", "name": "Active automations"},
        {"uri": "home://logs/recent", "name": "Recent logs"},
        {"uri": "home://sensors/environment", "name": "Temperature and humidity"},
    ]
    TOOL_DESCRIPTIONS = {
        "relay.turn_on": "릴레이 채널을 즉시 켭니다.",
        "relay.turn_off": "릴레이 채널을 즉시 끕니다.",
        "relay.get_state": "릴레이 장치의 현재 상태를 조회합니다.",
        "relay.schedule": "릴레이 채널 on/off 예약을 생성합니다.",
        "calendar.get_tomorrow": "내일 일정을 조회합니다.",
        "alarm.create": "알람을 생성하고 Home Assistant 알람 서비스에 전달합니다.",
        "alarm.update_profile": "기존 알람의 강도 프로필을 변경합니다.",
        "system.explain_recent_action": "최근 Tool 실행 로그를 바탕으로 동작 이유를 설명합니다.",
        "system.execute_due_schedules": "현재 시각 기준으로 만료된 예약을 실행합니다.",
        "automation.prepare_class_day": "내일 must_wake 일정 기준으로 수업일 알람을 준비합니다.",
        "system.status_summary": "릴레이·알람·예약·내일 일정 요약을 반환합니다.",
        "sensor.get_environment": "온도·습도 센서 값을 조회합니다.",
        "sensor.set_environment": "모의 센서 값을 갱신합니다 (개발/테스트).",
        "ha.call_service": "Home Assistant 서비스를 호출합니다 (예: light.turn_on).",
    }
    PROMPTS = {
        "create-alarm": "Create an alarm with a validated time, profile, and label.",
        "prepare-class-day": "Inspect tomorrow's calendar and strengthen wake-up profile if needed.",
        "schedule-relay": "Schedule a relay channel on/off action at a validated time.",
        "why-did-this-run": "Explain a recent automation from audit logs and policy state.",
        "status-summary": "Summarize relay, alarm, and active automation state.",
    }

    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orchestrator = orchestrator

    def list_resources(self) -> list[dict[str, str]]:
        return self.RESOURCES

    def read_resource(self, uri: str) -> dict[str, Any]:
        return self.orchestrator.read_resource(uri)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "description": self.TOOL_DESCRIPTIONS[name],
                "inputSchema": TOOL_SCHEMAS[name],
            }
            for name in self.TOOL_DESCRIPTIONS
        ]

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.orchestrator.call_tool(name, arguments or {}, source="mcp")

    def list_prompts(self) -> list[dict[str, str]]:
        return [{"name": name, "description": description} for name, description in self.PROMPTS.items()]

    def get_prompt(self, name: str) -> dict[str, str]:
        if name not in self.PROMPTS:
            raise ValueError(f"Unknown prompt: {name}")
        return {"name": name, "description": self.PROMPTS[name]}
