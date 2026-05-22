from __future__ import annotations

from ..store import InMemoryStore
from .camera_stream import CameraStreamService
from .scene_analyzer import SceneAnalyzer, snapshot_to_dict


class SceneService:
    def __init__(self, store: InMemoryStore, camera: CameraStreamService | None = None) -> None:
        self.store = store
        self.camera = camera or CameraStreamService(store)
        self._standalone_analyzer = SceneAnalyzer()

    def get_latest(self) -> dict | None:
        snapshot = self.store.latest_scene
        if snapshot is None:
            return None
        return snapshot_to_dict(snapshot)

    def analyze_bytes(self, data: bytes) -> dict:
        snapshot = self.camera.analyze_bytes(data)
        return snapshot_to_dict(snapshot)

    def analyze_frame_array(self, frame) -> dict:
        """Analyze a BGR numpy frame (used in unit tests)."""
        snapshot = self._standalone_analyzer.analyze_frame(frame)
        self.store.latest_scene = snapshot
        return snapshot_to_dict(snapshot)
