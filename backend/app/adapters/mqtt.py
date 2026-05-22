from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MqttRelayPublisher:
    host: str
    port: int
    topic_prefix: str = "home"
    username: str | None = None
    password: str | None = None
    dry_run: bool = True

    def command_topic(self, device_id: str, channel: str) -> str:
        return f"{self.topic_prefix}/relay/{device_id}/{channel}/set"

    def state_topic(self, device_id: str) -> str:
        return f"{self.topic_prefix}/relay/{device_id}/state"

    def availability_topic(self, device_id: str) -> str:
        return f"{self.topic_prefix}/relay/{device_id}/availability"

    def publish_relay_command(self, device_id: str, channel: str, action: str) -> dict[str, Any]:
        topic = self.command_topic(device_id, channel)
        if self.dry_run:
            return {"published": False, "dry_run": True, "topic": topic, "payload": action}

        try:
            import paho.mqtt.client as mqtt  # type: ignore
        except ImportError as exc:
            raise RuntimeError("paho-mqtt is required for live MQTT publishing") from exc

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.username:
            client.username_pw_set(self.username, self.password)
        client.connect(self.host, self.port, keepalive=30)
        client.publish(topic, action, qos=1, retain=False)
        client.disconnect()
        return {"published": True, "dry_run": False, "topic": topic, "payload": action}
