from __future__ import annotations

from datetime import datetime
from typing import Any


class ToolValidationError(ValueError):
    def __init__(self, tool_name: str, errors: list[str]) -> None:
        self.tool_name = tool_name
        self.errors = errors
        super().__init__("; ".join(errors))


TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "relay.turn_on": {
        "type": "object",
        "required": ["channel"],
        "properties": {
            "device_id": {"type": "string"},
            "channel": {"type": "string", "enum": ["ch1", "ch2"]},
        },
        "additionalProperties": False,
    },
    "relay.turn_off": {
        "type": "object",
        "required": ["channel"],
        "properties": {
            "device_id": {"type": "string"},
            "channel": {"type": "string", "enum": ["ch1", "ch2"]},
        },
        "additionalProperties": False,
    },
    "relay.get_state": {
        "type": "object",
        "required": [],
        "properties": {"device_id": {"type": "string"}},
        "additionalProperties": False,
    },
    "relay.schedule": {
        "type": "object",
        "required": ["channel", "action", "execute_at"],
        "properties": {
            "device_id": {"type": "string"},
            "channel": {"type": "string", "enum": ["ch1", "ch2"]},
            "action": {"type": "string", "enum": ["on", "off"]},
            "execute_at": {"type": "string", "format": "date-time"},
        },
        "additionalProperties": False,
    },
    "calendar.get_tomorrow": {
        "type": "object",
        "required": [],
        "properties": {},
        "additionalProperties": False,
    },
    "alarm.create": {
        "type": "object",
        "required": ["time", "profile", "label"],
        "properties": {
            "time": {"type": "string", "format": "date-time"},
            "profile": {"type": "string", "minLength": 1},
            "label": {"type": "string", "minLength": 1},
            "linked_event_id": {"type": ["string", "null"]},
        },
        "additionalProperties": False,
    },
    "alarm.update_profile": {
        "type": "object",
        "required": ["alarm_id", "profile"],
        "properties": {
            "alarm_id": {"type": "string", "minLength": 1},
            "profile": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    },
    "system.explain_recent_action": {
        "type": "object",
        "required": [],
        "properties": {"time_window": {"type": "string"}},
        "additionalProperties": False,
    },
    "system.execute_due_schedules": {
        "type": "object",
        "required": [],
        "properties": {"now": {"type": "string", "format": "date-time"}},
        "additionalProperties": False,
    },
}


def validate_tool_input(tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    schema = TOOL_SCHEMAS.get(tool_name)
    if not schema:
        raise ToolValidationError(tool_name, [f"Unknown tool: {tool_name}"])
    errors: list[str] = []
    required = set(schema.get("required", []))
    properties: dict[str, Any] = schema.get("properties", {})

    missing = sorted(required - set(payload))
    for field in missing:
        errors.append(f"Missing required field: {field}")

    if not schema.get("additionalProperties", True):
        for field in sorted(set(payload) - set(properties)):
            errors.append(f"Unexpected field: {field}")

    for field, value in payload.items():
        if field not in properties:
            continue
        field_schema = properties[field]
        expected_type = field_schema.get("type")
        if not _matches_type(value, expected_type):
            errors.append(f"Invalid type for {field}: expected {expected_type}")
            continue
        if "enum" in field_schema and value not in field_schema["enum"]:
            errors.append(f"Invalid value for {field}: {value}")
        if field_schema.get("minLength") and isinstance(value, str) and len(value.strip()) < field_schema["minLength"]:
            errors.append(f"{field} must not be empty")
        if field_schema.get("format") == "date-time" and isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{field} must be ISO date-time")

    if errors:
        raise ToolValidationError(tool_name, errors)
    return payload


def _matches_type(value: Any, expected_type: Any) -> bool:
    if isinstance(expected_type, list):
        return any(_matches_type(value, item) for item in expected_type)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "null":
        return value is None
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return True
