from __future__ import annotations

from typing import Any

from ..adapters.calendar import CalendarAdapter, FileCalendarAdapter, NaverCalendarReadAdapter
from ..adapters.home_assistant import HomeAssistantClient
from ..adapters.mqtt import MqttRelayPublisher
from ..adapters.relay import InMemoryRelayAdapter
from ..config import Settings
from ..schemas.models import ToolResult, to_jsonable
from ..store import InMemoryStore
from .alarm import AlarmService
from .audit import AuditLog
from .automation import AutomationService
from .policies import PolicyRegistry
from .scheduler import SchedulerService
from .validation import ToolValidationError, validate_tool_input


class Orchestrator:
    def __init__(
        self,
        settings: Settings,
        store: InMemoryStore | None = None,
        calendar_adapter: CalendarAdapter | None = None,
    ) -> None:
        self.settings = settings
        self.settings.ensure_runtime_dirs()
        self.store = store or InMemoryStore(default_device_id=settings.default_device_id)
        self.policies = PolicyRegistry(settings.policies_dir)
        self.policies.load()
        self.relay = InMemoryRelayAdapter(self.store)
        self.mqtt = MqttRelayPublisher(
            host=settings.mqtt_host,
            port=settings.mqtt_port,
            topic_prefix=settings.mqtt_topic_prefix,
            username=settings.mqtt_username,
            password=settings.mqtt_password,
            dry_run=settings.env != "prod",
        )
        self.home_assistant = HomeAssistantClient(
            base_url=settings.home_assistant_url,
            token=settings.home_assistant_token,
            alarm_service=settings.home_assistant_alarm_service,
            dry_run=settings.env != "prod",
        )
        self.calendar = calendar_adapter or self._calendar_from_settings(settings)
        self.scheduler = SchedulerService(self.store, self.relay)
        self.scheduler.command_executor = self._execute_scheduled_relay_command
        self.alarm = AlarmService(self.store, self.home_assistant, self.policies)
        self.automation = AutomationService(self.calendar, self.alarm, settings.timezone)
        self.audit = AuditLog(settings.data_dir / "audit.jsonl")

    def read_resource(self, uri: str) -> dict[str, Any]:
        if uri == "home://devices/relay":
            return {"relays": [to_jsonable(state) for state in self.store.relays.values()]}
        if uri == "home://calendar/tomorrow":
            return {"events": [to_jsonable(event) for event in self.calendar.get_tomorrow(self.settings.timezone)]}
        if uri == "home://alarm/next":
            return {"alarm": to_jsonable(self.alarm.next_alarm()) if self.alarm.next_alarm() else None}
        if uri == "home://automation/active":
            return {"schedules": [to_jsonable(job) for job in self.store.schedules.values() if job.status == "pending"]}
        if uri == "home://logs/recent":
            return {"events": self.audit.recent()}
        raise ValueError(f"Unknown resource URI: {uri}")

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        *,
        actor: str = "system",
        source: str = "api",
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        args = arguments or {}
        try:
            args = validate_tool_input(tool_name, args)
            result = self._dispatch_tool(tool_name, args)
            payload = ToolResult(success=True, data=result).to_dict()
        except ToolValidationError as exc:
            payload = ToolResult(
                success=False,
                data={"error_code": "validation_error", "validation_errors": exc.errors},
                error=str(exc),
            ).to_dict()
        except Exception as exc:
            payload = ToolResult(
                success=False,
                data={"error_code": "execution_failed"},
                error=str(exc),
            ).to_dict()

        self.audit.record(
            actor=actor,
            source=source,
            tool_name=tool_name,
            validated_input=args,
            result=payload,
            correlation_id=correlation_id,
        )
        return payload

    def explain_recent_action(self, time_window: str = "24h") -> str:
        events = self.audit.recent(limit=10)
        if not events:
            return f"No recent audited actions found for window {time_window}."
        latest = events[-1]
        return (
            f"Latest action was {latest['tool_name']} from {latest['source']} by {latest['actor']} "
            f"at {latest['timestamp']}. Result success={latest['result'].get('success')}."
        )

    def _dispatch_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "relay.turn_on":
            return self._relay_set(args, "on")
        if tool_name == "relay.turn_off":
            return self._relay_set(args, "off")
        if tool_name == "relay.get_state":
            device_id = str(args.get("device_id") or self.settings.default_device_id)
            return {"state": to_jsonable(self.relay.get_state(device_id))}
        if tool_name == "relay.schedule":
            job = self.scheduler.create_relay_schedule(
                device_id=str(args.get("device_id") or self.settings.default_device_id),
                channel=str(args["channel"]),
                action=str(args["action"]),
                execute_at=str(args["execute_at"]),
            )
            return {"job_id": job.job_id, "accepted": True, "job": to_jsonable(job)}
        if tool_name == "calendar.get_tomorrow":
            return {"events": [to_jsonable(event) for event in self.calendar.get_tomorrow(self.settings.timezone)]}
        if tool_name == "alarm.create":
            alarm = self.alarm.create(
                time=str(args["time"]),
                profile=str(args["profile"]),
                label=str(args["label"]),
                linked_event_id=args.get("linked_event_id"),
            )
            return {"alarm_id": alarm.alarm_id, "alarm": to_jsonable(alarm)}
        if tool_name == "alarm.update_profile":
            alarm = self.alarm.update_profile(alarm_id=str(args["alarm_id"]), profile=str(args["profile"]))
            return {"updated": True, "alarm": to_jsonable(alarm)}
        if tool_name == "system.explain_recent_action":
            return {"explanation": self.explain_recent_action(str(args.get("time_window", "24h")))}
        if tool_name == "system.execute_due_schedules":
            executed = self.scheduler.execute_due(args.get("now"))
            return {"executed": [to_jsonable(job) for job in executed]}
        if tool_name == "automation.prepare_class_day":
            profile = str(args.get("profile", "aggressive"))
            offset_min = int(args.get("offset_min", 30))
            return self.automation.prepare_class_day(profile=profile, offset_min=offset_min)
        if tool_name == "system.status_summary":
            return self._status_summary()
        raise ValueError(f"Unknown tool: {tool_name}")

    def _status_summary(self) -> dict[str, Any]:
        next_alarm = self.alarm.next_alarm()
        return {
            "relays": [to_jsonable(state) for state in self.store.relays.values()],
            "pending_schedules": len([job for job in self.store.schedules.values() if job.status == "pending"]),
            "alarms": len(self.store.alarms),
            "next_alarm": to_jsonable(next_alarm) if next_alarm else None,
            "tomorrow_events": len(self.calendar.get_tomorrow(self.settings.timezone)),
        }

    def _relay_set(self, args: dict[str, Any], action: str) -> dict[str, Any]:
        device_id = str(args.get("device_id") or self.settings.default_device_id)
        channel = str(args["channel"])
        state = self.relay.set_channel(device_id, channel, action)
        mqtt_result = self.mqtt.publish_relay_command(device_id, channel, action)
        return {"state": to_jsonable(state), "mqtt": mqtt_result}

    def _execute_scheduled_relay_command(self, job) -> dict[str, Any]:
        result = self._relay_set(
            {"device_id": job.device_id, "channel": job.channel},
            job.action,
        )
        self.audit.record(
            actor="scheduler",
            source="scheduler",
            tool_name=f"relay.turn_{job.action}",
            validated_input={
                "job_id": job.job_id,
                "device_id": job.device_id,
                "channel": job.channel,
                "action": job.action,
                "execute_at": job.execute_at,
            },
            result={"success": True, "data": result},
            correlation_id=job.job_id,
        )
        return result

    @staticmethod
    def _calendar_from_settings(settings: Settings) -> CalendarAdapter:
        if settings.calendar_provider == "file":
            return FileCalendarAdapter(settings.calendar_file)
        if settings.calendar_provider == "naver":
            return NaverCalendarReadAdapter()
        raise ValueError(f"Unsupported calendar provider: {settings.calendar_provider}")
