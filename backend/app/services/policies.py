from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .validation import TOOL_SCHEMAS


@dataclass
class PolicyDocument:
    path: Path
    data: dict[str, Any]


class PolicyRegistry:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.documents: list[PolicyDocument] = []

    def load(self) -> list[PolicyDocument]:
        self.documents = []
        if not self.root.exists():
            return self.documents
        for path in sorted(self.root.rglob("*.yaml")):
            data = _load_yaml_subset(path)
            self.documents.append(PolicyDocument(path=path, data=data))
        return self.documents

    def validate(self) -> list[str]:
        errors: list[str] = []
        seen_profiles: set[str] = set()
        for doc in self.documents:
            name = doc.path.name
            data = doc.data
            if "alarm_profiles" in doc.path.parts:
                profile_id = data.get("profile_id")
                if not profile_id:
                    errors.append(f"{name}: missing profile_id")
                elif profile_id in seen_profiles:
                    errors.append(f"{name}: duplicate profile_id {profile_id}")
                else:
                    seen_profiles.add(str(profile_id))
            if "automation_rules" in doc.path.parts:
                if not data.get("rule_id"):
                    errors.append(f"{name}: missing rule_id")
                for action in data.get("actions", []):
                    if action not in TOOL_SCHEMAS:
                        errors.append(f"{name}: unknown action {action}")
            if "relay_defaults" in doc.path.parts:
                if not data.get("device_id"):
                    errors.append(f"{name}: missing device_id")
                for channel in data.get("channels", []):
                    if channel not in {"ch1", "ch2"}:
                        errors.append(f"{name}: invalid relay channel {channel}")
        return errors

    def profile_ids(self) -> set[str]:
        if not self.documents:
            self.load()
        return {
            str(doc.data["profile_id"])
            for doc in self.documents
            if "alarm_profiles" in doc.path.parts and doc.data.get("profile_id")
        }


def _load_yaml_subset(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return _simple_yaml_parse(path.read_text(encoding="utf-8"))

    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Policy must be a YAML mapping: {path}")
    return loaded


def _simple_yaml_parse(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                data[key] = []
                current_list_key = key
            else:
                data[key] = _coerce_scalar(value)
                current_list_key = None
            continue
        if current_list_key and re.match(r"^\s*-\s+", line):
            item = re.sub(r"^\s*-\s+", "", line).strip()
            data[current_list_key].append(_coerce_scalar(item))
    return data


def _coerce_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.isdigit():
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value
