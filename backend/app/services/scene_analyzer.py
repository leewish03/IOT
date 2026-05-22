from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from ..schemas.models import PersonSceneInfo, SceneSnapshot, utcnow_iso


class SceneAnalyzer:
    """OpenCV-based scene analysis without sending raw images to an LLM."""

    _MOTION_THRESHOLD = 12.0
    _HOG_WIN_STRIDE = (8, 8)
    _HOG_PADDING = (16, 16)
    _HOG_SCALE = 1.05

    def __init__(self) -> None:
        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self._prev_gray: np.ndarray | None = None

    def analyze_frame(
        self,
        frame_bgr: np.ndarray,
        *,
        previous_gray: np.ndarray | None = None,
    ) -> SceneSnapshot:
        if frame_bgr is None or frame_bgr.size == 0:
            raise ValueError("Empty frame")

        height, width = frame_bgr.shape[:2]
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        prev = previous_gray if previous_gray is not None else self._prev_gray
        global_motion = self._detect_global_motion(gray, prev)

        rects, _weights = self._detect_people(frame_bgr)

        persons: list[PersonSceneInfo] = []
        for x, y, w, h in rects:
            x_i, y_i, w_i, h_i = int(x), int(y), int(w), int(h)
            cx = (x_i + w_i / 2.0) / max(width, 1)
            cy = (y_i + h_i / 2.0) / max(height, 1)
            activity = self._person_activity(gray, x_i, y_i, w_i, h_i, prev)
            persons.append(
                PersonSceneInfo(
                    bbox=[x_i, y_i, w_i, h_i],
                    centroid={"x": round(cx, 4), "y": round(cy, 4)},
                    posture=self._infer_posture(w_i, h_i),
                    activity=activity,
                    zone=self._zone_from_centroid(cx, cy),
                )
            )

        self._prev_gray = gray
        motion = global_motion
        if persons and any(p.activity == "moving" for p in persons):
            motion = "moving"

        return SceneSnapshot(
            person_count=len(persons),
            persons=persons,
            motion=motion,
            summary_ko=self._build_summary_ko(len(persons), persons, motion),
            analyzed_at=utcnow_iso(),
            frame_width=width,
            frame_height=height,
        )

    def reset_motion_state(self) -> None:
        self._prev_gray = None

    def _detect_people(self, frame_bgr: np.ndarray) -> tuple[Any, Any]:
        return self._hog.detectMultiScale(
            frame_bgr,
            winStride=self._HOG_WIN_STRIDE,
            padding=self._HOG_PADDING,
            scale=self._HOG_SCALE,
        )

    @staticmethod
    def decode_image_bytes(data: bytes) -> np.ndarray:
        arr = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Could not decode image bytes")
        return frame

    @staticmethod
    def decode_base64_image(data_b64: str) -> np.ndarray:
        import base64

        raw = base64.b64decode(data_b64, validate=True)
        return SceneAnalyzer.decode_image_bytes(raw)

    def _detect_global_motion(self, gray: np.ndarray, prev_gray: np.ndarray | None) -> str:
        if prev_gray is None or prev_gray.shape != gray.shape:
            return "still"
        diff = cv2.absdiff(gray, prev_gray)
        score = float(np.mean(diff))
        return "moving" if score >= self._MOTION_THRESHOLD else "still"

    def _person_activity(
        self,
        gray: np.ndarray,
        x: int,
        y: int,
        w: int,
        h: int,
        prev_gray: np.ndarray | None,
    ) -> str:
        if prev_gray is None or prev_gray.shape != gray.shape:
            return "still"
        roi = gray[y : y + h, x : x + w]
        prev_roi = prev_gray[y : y + h, x : x + w]
        if roi.size == 0 or prev_roi.size == 0:
            return "still"
        score = float(np.mean(cv2.absdiff(roi, prev_roi)))
        return "moving" if score >= self._MOTION_THRESHOLD else "still"

    @staticmethod
    def _infer_posture(width: int, height: int) -> str:
        if width <= 0 or height <= 0:
            return "unknown"
        ratio = height / float(width)
        if ratio >= 2.2:
            return "standing"
        if ratio <= 1.6:
            return "sitting"
        return "unknown"

    @staticmethod
    def _zone_from_centroid(cx: float, cy: float) -> str:
        col = "left" if cx < 0.33 else "center" if cx < 0.67 else "right"
        row = "top" if cy < 0.33 else "middle" if cy < 0.67 else "bottom"
        return f"{row}_{col}"

    @staticmethod
    def _build_summary_ko(person_count: int, persons: list[PersonSceneInfo], motion: str) -> str:
        if person_count == 0:
            motion_ko = "움직임 감지됨" if motion == "moving" else "정적 장면"
            return f"사람이 감지되지 않았습니다. ({motion_ko})"
        zones = ", ".join(sorted({p.zone for p in persons}))
        postures = ", ".join(sorted({p.posture for p in persons}))
        moving = sum(1 for p in persons if p.activity == "moving")
        return (
            f"{person_count}명 감지, 구역: {zones}, 자세: {postures}, "
            f"움직이는 대상 {moving}명, 전체 장면 {motion}."
        )


def snapshot_to_dict(snapshot: SceneSnapshot) -> dict[str, Any]:
    from ..schemas.models import to_jsonable

    return to_jsonable(snapshot)
