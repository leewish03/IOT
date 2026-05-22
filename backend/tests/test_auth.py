from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from backend.app.config import Settings
from backend.app.main import app
from backend.app.services.orchestrator import Orchestrator


class AuthEnforcementTests(unittest.TestCase):
    def setUp(self) -> None:
        if app is None:
            self.skipTest("FastAPI not installed")
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        policy_root = root / "policies"
        (policy_root / "alarm_profiles").mkdir(parents=True)
        (policy_root / "alarm_profiles" / "normal.yaml").write_text(
            "profile_id: normal\nsteps:\n  - notify_mobile\n",
            encoding="utf-8",
        )
        data_dir = root / "data"
        data_dir.mkdir()
        self.settings = Settings(
            env="local",
            backend_api_token="prod-secret",
            data_dir=data_dir,
            policies_dir=policy_root,
        )
        self.settings.ensure_runtime_dirs()
        import backend.app.main as main_module
        from backend.app.mcp_server import McpCatalogServer

        self.orchestrator = Orchestrator(self.settings)
        main_module.settings = self.settings
        main_module.orchestrator = self.orchestrator
        main_module.mcp_catalog = McpCatalogServer(self.orchestrator)
        main_module.scene_service = self.orchestrator.scene
        from fastapi.testclient import TestClient

        self.client = TestClient(main_module.app)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_public_routes_without_bearer(self) -> None:
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/tools").status_code, 200)

    def test_protected_routes_reject_missing_token(self) -> None:
        self.assertEqual(self.client.get("/scene/latest").status_code, 401)
        self.assertEqual(
            self.client.post("/tools/relay.turn_on", json={"channel": "ch1"}).status_code,
            401,
        )

    def test_protected_routes_accept_valid_bearer(self) -> None:
        headers = {"Authorization": "Bearer prod-secret"}
        self.assertEqual(self.client.get("/scene/latest", headers=headers).status_code, 404)
        response = self.client.post(
            "/tools/relay.turn_on",
            json={"channel": "ch1"},
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_validate_security_rejects_default_token_in_prod(self) -> None:
        bad = Settings(env="production", backend_api_token="change-me")
        with self.assertRaises(RuntimeError):
            bad.validate_security()


if __name__ == "__main__":
    unittest.main()
