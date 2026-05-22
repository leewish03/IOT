from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from backend.app.config import Settings
from backend.app.main import app


@unittest.skipUnless(app is not None, "fastapi is required for API integration tests")
class ApiIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        policy_root = root / "policies"
        (policy_root / "alarm_profiles").mkdir(parents=True)
        (policy_root / "alarm_profiles" / "normal.yaml").write_text(
            "profile_id: normal\nsteps:\n  - notify_mobile\n",
            encoding="utf-8",
        )
        (policy_root / "alarm_profiles" / "aggressive.yaml").write_text(
            "profile_id: aggressive\nsteps:\n  - notify_mobile\n  - lights_on\n",
            encoding="utf-8",
        )
        data_dir = root / "data"
        data_dir.mkdir()
        tz = ZoneInfo("Asia/Seoul")
        tomorrow = (datetime.now(tz).date() + timedelta(days=1)).isoformat()
        (data_dir / "calendar_events.json").write_text(
            json.dumps(
                {
                    "events": [
                        {
                            "event_id": "api-1",
                            "title": "API Test Class",
                            "start": f"{tomorrow}T10:00:00+09:00",
                            "must_wake": True,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        import backend.app.main as main_module

        self.settings = Settings(
            data_dir=data_dir,
            policies_dir=policy_root,
            calendar_file=data_dir / "calendar_events.json",
        )
        main_module.settings = self.settings
        main_module.settings.ensure_runtime_dirs()
        main_module.orchestrator = __import__(
            "backend.app.services.orchestrator", fromlist=["Orchestrator"]
        ).Orchestrator(self.settings)
        main_module.mcp_catalog = __import__(
            "backend.app.mcp_server", fromlist=["McpCatalogServer"]
        ).McpCatalogServer(main_module.orchestrator)

        from fastapi.testclient import TestClient

        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_health_and_mcp_surface(self) -> None:
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")

        tools = self.client.get("/tools")
        self.assertEqual(tools.status_code, 200)
        names = {item["name"] for item in tools.json()}
        self.assertIn("automation.prepare_class_day", names)
        self.assertIn("system.status_summary", names)

    def test_relay_tool_via_http(self) -> None:
        response = self.client.post("/tools/relay.turn_on", json={"channel": "ch1"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        resource = self.client.get("/resource", params={"uri": "home://devices/relay"})
        self.assertEqual(resource.status_code, 200)
        self.assertTrue(resource.json()["relays"][0]["channels"]["ch1"])

    def test_prepare_class_day_via_http(self) -> None:
        response = self.client.post(
            "/tools/automation.prepare_class_day",
            json={"profile": "aggressive", "offset_min": 30},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertTrue(body["data"]["prepared"])


if __name__ == "__main__":
    unittest.main()
