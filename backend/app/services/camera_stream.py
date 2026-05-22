from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from collections.abc import Callable
from typing import Any

from ..schemas.models import SceneSnapshot
from ..store import InMemoryStore
from .scene_analyzer import SceneAnalyzer, snapshot_to_dict

logger = logging.getLogger(__name__)


def _parse_camera_device(raw: str | None) -> int | str | None:
    if not raw or not raw.strip():
        return None
    value = raw.strip()
    if value.isdigit():
        return int(value)
    if value.startswith("rtsp://") or value.startswith("http://") or value.startswith("https://"):
        return value
    return value


class CameraStreamService:
    """Optional background capture from CAMERA_DEVICE with rate-limited scene analysis."""

    def __init__(
        self,
        store: InMemoryStore,
        *,
        device: int | str | None = None,
        fps_limit: float | None = None,
        on_update: Callable[[SceneSnapshot], None] | None = None,
    ) -> None:
        self.store = store
        self.device = device if device is not None else _parse_camera_device(os.getenv("CAMERA_DEVICE"))
        if fps_limit is not None:
            self.fps_limit = fps_limit
        else:
            raw_fps = os.getenv("SCENE_FPS_LIMIT") or os.getenv("SCENE_FPS") or "1.0"
            self.fps_limit = float(raw_fps)
        self.on_update = on_update
        self._analyzer = SceneAnalyzer()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._subscribers: list[asyncio.Queue[dict[str, Any]]] = []

    @property
    def enabled(self) -> bool:
        return self.device is not None

    def latest(self) -> SceneSnapshot | None:
        return self.store.latest_scene

    def analyze_bytes(self, data: bytes) -> SceneSnapshot:
        frame = SceneAnalyzer.decode_image_bytes(data)
        snapshot = self._analyzer.analyze_frame(frame)
        self._publish(snapshot)
        return snapshot

    def _publish(self, snapshot: SceneSnapshot) -> None:
        with self._lock:
            self.store.latest_scene = snapshot
        if self.on_update:
            self.on_update(snapshot)
        payload = snapshot_to_dict(snapshot)
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=8)
        self._subscribers.append(queue)
        latest = self.latest()
        if latest is not None:
            try:
                queue.put_nowait(snapshot_to_dict(latest))
            except asyncio.QueueFull:
                pass
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def start(self) -> None:
        if not self.enabled or self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._capture_loop, name="camera-stream", daemon=True)
        self._thread.start()
        logger.info("Camera stream started for device=%s", self.device)

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        logger.info("Camera stream stopped")

    def _capture_loop(self) -> None:
        import cv2

        cap = cv2.VideoCapture(self.device)
        if not cap.isOpened():
            logger.warning("Could not open camera device %s", self.device)
            return
        interval = 1.0 / max(self.fps_limit, 0.1)
        try:
            while not self._stop.is_set():
                started = time.monotonic()
                ok, frame = cap.read()
                if not ok or frame is None:
                    time.sleep(interval)
                    continue
                try:
                    snapshot = self._analyzer.analyze_frame(frame)
                    self._publish(snapshot)
                except Exception:
                    logger.exception("Scene analysis failed on camera frame")
                elapsed = time.monotonic() - started
                time.sleep(max(0.0, interval - elapsed))
        finally:
            cap.release()
