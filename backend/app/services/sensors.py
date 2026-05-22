from __future__ import annotations

from ..schemas.models import EnvironmentSnapshot, utcnow_iso
from ..store import InMemoryStore


class SensorService:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def read_environment(self) -> EnvironmentSnapshot:
        return self.store.environment

    def update_environment(self, temperature_c: float | None = None, humidity_pct: float | None = None) -> EnvironmentSnapshot:
        env = self.store.environment
        if temperature_c is not None:
            env.temperature_c = temperature_c
        if humidity_pct is not None:
            env.humidity_pct = humidity_pct
        env.updated_at = utcnow_iso()
        return env
