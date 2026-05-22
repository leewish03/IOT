from __future__ import annotations

import base64
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from backend.app.config import Settings
from backend.app.services.orchestrator import Orchestrator
from backend.app.services.scene import SceneService
from backend.app.services.scene_analyzer import SceneAnalyzer
from backend.app.store import InMemoryStore


def _synthetic_bgr(width: int = 320, height: int = 240, fill: int = 40) -> np.ndarray:
    frame = np.full((height, width, 3), fill, dtype=np.uint8)
    cv2 = __import__("cv2")
    cv2.rectangle(frame, (120, 60), (200, 200), (180, 180, 180), -1)
    return frame


def _encode_png(frame: np.ndarray) -> bytes:
    cv2 = __import__("cv2")
    ok, buf = cv2.imencode(".png", frame)
    assert ok
    return buf.tobytes()


class SceneAnalyzerTests(unittest.TestCase):
    def test_empty_frame_raises(self) -> None:
        analyzer = SceneAnalyzer()
        with self.assertRaises(ValueError):
            analyzer.analyze_frame(np.array([]))

    def test_analyze_static_frame_structure(self) -> None:
        analyzer = SceneAnalyzer()
        frame = _synthetic_bgr()
        snapshot = analyzer.analyze_frame(frame)
        self.assertEqual(snapshot.person_count, 0)
        self.assertEqual(snapshot.motion, "still")
        self.assertEqual(snapshot.frame_width, 320)
        self.assertEqual(snapshot.frame_height, 240)
        self.assertIn("사람이 감지되지 않았습니다", snapshot.summary_ko)

    def test_global_motion_between_frames(self) -> None:
        analyzer = SceneAnalyzer()
        frame_a = _synthetic_bgr(fill=20)
        frame_b = _synthetic_bgr(fill=200)
        gray_a = __import__("cv2").cvtColor(frame_a, __import__("cv2").COLOR_BGR2GRAY)
        snapshot = analyzer.analyze_frame(frame_b, previous_gray=gray_a)
        self.assertEqual(snapshot.motion, "moving")

    def test_zone_and_posture_helpers(self) -> None:
        self.assertEqual(SceneAnalyzer._zone_from_centroid(0.1, 0.8), "bottom_left")
        self.assertEqual(SceneAnalyzer._infer_posture(40, 120), "standing")
        self.assertEqual(SceneAnalyzer._infer_posture(120, 160), "sitting")

    def test_person_detection_with_mock_hog(self) -> None:
        analyzer = SceneAnalyzer()
        frame = _synthetic_bgr()
        fake_rect = np.array([[100, 50, 60, 140]], dtype=np.float32)
        with patch.object(analyzer, "_detect_people", return_value=(fake_rect, None)):
            snapshot = analyzer.analyze_frame(frame)
        self.assertEqual(snapshot.person_count, 1)
        person = snapshot.persons[0]
        self.assertEqual(person.bbox, [100, 50, 60, 140])
        self.assertEqual(person.posture, "standing")
        self.assertIn("_", person.zone)


class SceneServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore(default_device_id="test-device")
        self.service = SceneService(self.store)

    def test_analyze_bytes_updates_latest(self) -> None:
        png = _encode_png(_synthetic_bgr())
        result = self.service.analyze_bytes(png)
        self.assertEqual(result["person_count"], 0)
        self.assertEqual(result["motion"], "still")
        latest = self.service.get_latest()
        assert latest is not None
        self.assertEqual(latest["analyzed_at"], result["analyzed_at"])

    def test_analyze_frame_array(self) -> None:
        result = self.service.analyze_frame_array(_synthetic_bgr())
        self.assertIn("summary_ko", result)
        self.assertIsInstance(result["persons"], list)


class SceneOrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
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
        self.settings = Settings(data_dir=data_dir, policies_dir=policy_root)
        self.orchestrator = Orchestrator(self.settings)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_scene_tools(self) -> None:
        png = _encode_png(_synthetic_bgr())
        b64 = base64.b64encode(png).decode("ascii")
        analyzed = self.orchestrator.call_tool("scene.analyze", {"image_base64": b64})
        self.assertTrue(analyzed["success"])
        self.assertIn("scene", analyzed["data"])

        latest = self.orchestrator.call_tool("scene.get_latest", {})
        self.assertTrue(latest["success"])
        self.assertIsNotNone(latest["data"]["scene"])

        resource = self.orchestrator.read_resource("home://scene/latest")
        self.assertIsNotNone(resource["scene"])


@unittest.skipUnless(__import__("backend.app.main", fromlist=["app"]).app is not None, "fastapi required")
class SceneApiTests(unittest.TestCase):
    def setUp(self) -> None:
        import backend.app.main as main_module
        from fastapi.testclient import TestClient

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
        settings = Settings(data_dir=data_dir, policies_dir=policy_root)
        main_module.settings = settings
        main_module.settings.ensure_runtime_dirs()
        main_module.orchestrator = Orchestrator(settings)
        main_module.mcp_catalog = __import__(
            "backend.app.mcp_server", fromlist=["McpCatalogServer"]
        ).McpCatalogServer(main_module.orchestrator)
        main_module.scene_service = main_module.orchestrator.scene
        self.client = TestClient(main_module.app)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_scene_http_endpoints(self) -> None:
        latest = self.client.get("/scene/latest")
        self.assertEqual(latest.status_code, 404)

        png = _encode_png(_synthetic_bgr())
        response = self.client.post(
            "/scene/analyze",
            files={"file": ("frame.png", io.BytesIO(png), "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["person_count"], 0)
        self.assertIn("summary_ko", body)

        latest_ok = self.client.get("/scene/latest")
        self.assertEqual(latest_ok.status_code, 200)
        self.assertEqual(latest_ok.json()["person_count"], 0)

    def test_mcp_lists_scene_tools(self) -> None:
        tools = self.client.get("/tools")
        names = {item["name"] for item in tools.json()}
        self.assertIn("scene.get_latest", names)
        self.assertIn("scene.analyze", names)

    def test_scene_analyze_empty_upload_returns_400(self) -> None:
        response = self.client.post("/scene/analyze", files={"file": ("empty.png", io.BytesIO(b""), "image/png")})
        self.assertEqual(response.status_code, 400)

    def test_ws_scene_receives_snapshot_after_analyze(self) -> None:
        png = _encode_png(_synthetic_bgr())
        with self.client.websocket_connect("/ws/scene") as ws:
            self.client.post(
                "/scene/analyze",
                files={"file": ("frame.png", io.BytesIO(png), "image/png")},
            )
            payload = ws.receive_json()
            self.assertIn("person_count", payload)
            self.assertIn("summary_ko", payload)


if __name__ == "__main__":
    unittest.main()
