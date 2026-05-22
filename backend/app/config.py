from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    env: str = "local"
    timezone: str = "Asia/Seoul"
    data_dir: Path = Path("./data")
    policies_dir: Path = Path("./policies")
    default_device_id: str = "relay_esp12e_room_a"
    backend_api_token: str = "change-me"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_topic_prefix: str = "home"
    home_assistant_url: str = "http://homeassistant.local:8123"
    home_assistant_token: str = "change-me"
    home_assistant_alarm_service: str = "script.iot_alarm_run"
    calendar_provider: str = "file"
    calendar_file: Path = Path("./data/calendar_events.json")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            env=os.getenv("APP_ENV", "local"),
            timezone=os.getenv("APP_TIMEZONE", "Asia/Seoul"),
            data_dir=Path(os.getenv("APP_DATA_DIR", "./data")),
            policies_dir=Path(os.getenv("APP_POLICIES_DIR", "./policies")),
            default_device_id=os.getenv("APP_DEFAULT_DEVICE_ID", "relay_esp12e_room_a"),
            backend_api_token=os.getenv("BACKEND_API_TOKEN", "change-me"),
            mqtt_host=os.getenv("MQTT_HOST", "localhost"),
            mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
            mqtt_username=os.getenv("MQTT_USERNAME") or None,
            mqtt_password=os.getenv("MQTT_PASSWORD") or None,
            mqtt_topic_prefix=os.getenv("MQTT_TOPIC_PREFIX", "home"),
            home_assistant_url=os.getenv("HOME_ASSISTANT_URL", "http://homeassistant.local:8123"),
            home_assistant_token=os.getenv("HOME_ASSISTANT_TOKEN", "change-me"),
            home_assistant_alarm_service=os.getenv("HOME_ASSISTANT_ALARM_SERVICE", "script.iot_alarm_run"),
            calendar_provider=os.getenv("CALENDAR_PROVIDER", "file"),
            calendar_file=Path(os.getenv("CALENDAR_FILE", "./data/calendar_events.json")),
        )

    def ensure_runtime_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.policies_dir.mkdir(parents=True, exist_ok=True)

    def validate_security(self) -> None:
        if self.env != "local" and self.backend_api_token == "change-me":
            raise RuntimeError("BACKEND_API_TOKEN must be changed when APP_ENV is not local")
