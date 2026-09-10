"""JSON projection for workbench payloads. Does not invent domain facts."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any


def jsonable(value: Any, *, _depth: int = 0) -> Any:
    if _depth > 14:
        return "<truncated>"
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if is_dataclass(value) and not isinstance(value, type):
        payload: dict[str, Any] = {}
        for item in fields(value):
            raw = getattr(value, item.name)
            if item.name == "body" and isinstance(raw, str):
                payload["body_excerpt"] = raw[:480]
                continue
            payload[item.name] = jsonable(raw, _depth=_depth + 1)
        return payload
    if isinstance(value, dict):
        return {str(key): jsonable(val, _depth=_depth + 1) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(item, _depth=_depth + 1) for item in value]
    if hasattr(value, "to_dict"):
        return jsonable(value.to_dict(), _depth=_depth + 1)
    if hasattr(value, "as_dict"):
        return jsonable(value.as_dict(), _depth=_depth + 1)
    return str(value)
