from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from backend.app.adapters.calendar import FileCalendarAdapter, NaverCalendarReadAdapter
from backend.app.config import Settings
from backend.app.mcp_server import McpCatalogServer
from backend.app.services.policies import PolicyRegistry
from backend.app.services.orchestrator import Orchestrator


class OrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.policy_root = self.root / "policies"
        (self.policy_root / "alarm_profiles").mkdir(parents=True)
        (self.policy_root / "alarm_profiles" / "normal.yaml").write_text(
            "profile_id: normal\ndescription: test profile\nsteps:\n  - notify_mobile\n",
            encoding="utf-8",
        )
        self.data_dir = self.root / "data"
        self.data_dir.mkdir()
        self.settings = Settings(
            data_dir=self.data_dir,
            policies_dir=self.policy_root,
            calendar_file=self.data_dir / "calendar_events.json",
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_relay_turn_on_and_state_resource(self) -> None:
        orchestrator = Orchestrator(self.settings)
        result = orchestrator.call_tool("relay.turn_on", {"channel": "ch1"}, actor="user", source="test")

        self.assertTrue(result["success"])
        state = orchestrator.read_resource("home://devices/relay")["relays"][0]
        self.assertTrue(state["channels"]["ch1"])
        self.assertEqual(state["last_command_result"], "ch1:on")

    def test_relay_schedule_executes_centrally(self) -> None:
        orchestrator = Orchestrator(self.settings)
        execute_at = (
            datetime.now(UTC).replace(microsecond=0) - timedelta(seconds=1)
        ).isoformat().replace("+00:00", "Z")
        result = orchestrator.call_tool(
            "relay.schedule",
            {"channel": "ch2", "action": "off", "execute_at": execute_at},
        )

        self.assertTrue(result["success"])
        executed = orchestrator.scheduler.execute_due()
        self.assertEqual(len(executed), 1)
        self.assertEqual(executed[0].status, "executed")
        logs = orchestrator.read_resource("home://logs/recent")["events"]
        self.assertEqual(logs[-1]["actor"], "scheduler")

    def test_calendar_tomorrow_file_adapter(self) -> None:
        tomorrow = date.today() + timedelta(days=1)
        calendar_file = self.data_dir / "calendar_events.json"
        calendar_file.write_text(
            json.dumps(
                {
                    "events": [
                        {
                            "event_id": "evt-1",
                            "title": "Signals and Systems",
                            "start": f"{tomorrow.isoformat()}T09:00:00+09:00",
                            "must_wake": True,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        adapter = FileCalendarAdapter(calendar_file)
        orchestrator = Orchestrator(self.settings, calendar_adapter=adapter)

        result = orchestrator.call_tool("calendar.get_tomorrow", {})

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["events"][0]["title"], "Signals and Systems")
        self.assertTrue(result["data"]["events"][0]["must_wake"])

    def test_alarm_profile_validation_and_update(self) -> None:
        orchestrator = Orchestrator(self.settings)
        created = orchestrator.call_tool(
            "alarm.create",
            {"time": "2026-04-11T07:00:00+09:00", "profile": "normal", "label": "class_day"},
        )

        self.assertTrue(created["success"])
        alarm_id = created["data"]["alarm_id"]
        updated = orchestrator.call_tool("alarm.update_profile", {"alarm_id": alarm_id, "profile": "normal"})
        self.assertTrue(updated["success"])
        self.assertTrue(updated["data"]["updated"])

    def test_naver_read_adapter_fails_explicitly(self) -> None:
        with self.assertRaises(NotImplementedError):
            NaverCalendarReadAdapter().get_tomorrow()

    def test_invalid_channel_rejected_and_audited(self) -> None:
        orchestrator = Orchestrator(self.settings)
        result = orchestrator.call_tool("relay.turn_on", {"channel": "ch9"}, actor="user", source="test")

        self.assertFalse(result["success"])
        self.assertIn("Invalid value for channel", result["error"])
        logs = orchestrator.read_resource("home://logs/recent")["events"]
        self.assertEqual(logs[-1]["tool_name"], "relay.turn_on")
        self.assertEqual(logs[-1]["result"]["data"]["error_code"], "validation_error")

    def test_tool_rejects_unexpected_fields(self) -> None:
        orchestrator = Orchestrator(self.settings)
        result = orchestrator.call_tool("relay.turn_on", {"channel": "ch1", "extra": True})

        self.assertFalse(result["success"])
        self.assertIn("Unexpected field", result["error"])

    def test_relay_schedule_rejects_invalid_channel_and_action(self) -> None:
        orchestrator = Orchestrator(self.settings)
        execute_at = (
            datetime.now(UTC).replace(microsecond=0) + timedelta(minutes=5)
        ).isoformat().replace("+00:00", "Z")

        bad_channel = orchestrator.call_tool(
            "relay.schedule",
            {"channel": "ch9", "action": "off", "execute_at": execute_at},
        )
        bad_action = orchestrator.call_tool(
            "relay.schedule",
            {"channel": "ch1", "action": "toggle", "execute_at": execute_at},
        )

        self.assertFalse(bad_channel["success"])
        self.assertFalse(bad_action["success"])
        self.assertEqual(orchestrator.read_resource("home://automation/active")["schedules"], [])

    def test_execute_due_schedules_tool(self) -> None:
        orchestrator = Orchestrator(self.settings)
        execute_at = (
            datetime.now(UTC).replace(microsecond=0) - timedelta(seconds=1)
        ).isoformat().replace("+00:00", "Z")
        orchestrator.call_tool(
            "relay.schedule",
            {"channel": "ch1", "action": "on", "execute_at": execute_at},
        )

        result = orchestrator.call_tool("system.execute_due_schedules", {})

        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["executed"]), 1)

    def test_alarm_rejects_invalid_time(self) -> None:
        orchestrator = Orchestrator(self.settings)
        result = orchestrator.call_tool(
            "alarm.create",
            {"time": "tomorrow morning", "profile": "normal", "label": "class_day"},
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["data"]["error_code"], "validation_error")

    def test_next_alarm_is_chronological_across_offsets(self) -> None:
        orchestrator = Orchestrator(self.settings)
        later = (datetime.now(UTC) + timedelta(hours=3)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        sooner = (datetime.now(UTC) + timedelta(hours=1)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        first = orchestrator.call_tool("alarm.create", {"time": later, "profile": "normal", "label": "later"})
        second = orchestrator.call_tool("alarm.create", {"time": sooner, "profile": "normal", "label": "sooner"})

        self.assertTrue(first["success"])
        self.assertTrue(second["success"])
        next_alarm = orchestrator.read_resource("home://alarm/next")["alarm"]
        self.assertEqual(next_alarm["label"], "sooner")

    def test_mcp_catalog_exposes_tool_schemas(self) -> None:
        catalog = McpCatalogServer(Orchestrator(self.settings))
        tools = catalog.list_tools()

        self.assertIn("relay.schedule", {tool["name"] for tool in tools})
        for tool in tools:
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)

    def test_real_policy_samples_validate(self) -> None:
        registry = PolicyRegistry(Path("policies"))
        registry.load()

        self.assertEqual(registry.validate(), [])


if __name__ == "__main__":
    unittest.main()
