"""Append-only audit trail of agent-loop activity.

Every chat turn appends one JSON record to output/audit_trail.json with a timestamp,
the tools the agent called (with short args and a short result), and the stop reason.
The file is never wiped between runs — new records are appended to the existing array.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"

_MAX_STR = 200  # cap any single arg/result string so the trail stays short


def _short(value: Any) -> Any:
    """Shorten a value for the trail: truncate long strings, trim big containers,
    and reduce Pydantic models / other objects to JSON-safe forms."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value if len(value) <= _MAX_STR else value[:_MAX_STR] + "…"
    if hasattr(value, "model_dump"):  # Pydantic model
        return _short(value.model_dump())
    if isinstance(value, dict):
        return {str(k): _short(v) for k, v in list(value.items())[:12]}
    if isinstance(value, (list, tuple)):
        shortened = [_short(v) for v in value[:6]]
        if len(value) > 6:
            shortened.append(f"…(+{len(value) - 6} more)")
        return shortened
    text = str(value)
    return text if len(text) <= _MAX_STR else text[:_MAX_STR] + "…"


def extract_tool_calls(messages: list) -> list[dict]:
    """Pull tool calls + their results out of a PydanticAI run's message history."""
    calls: dict[str, dict] = {}
    order: list[str] = []
    for message in messages:
        for part in getattr(message, "parts", []):
            kind = part.__class__.__name__
            if kind == "ToolCallPart":
                # Skip PydanticAI's internal structured-output tool; keep real shop tools.
                if part.tool_name in {"final_result"}:
                    continue
                tool_id = getattr(part, "tool_call_id", None) or f"{part.tool_name}:{len(order)}"
                calls[tool_id] = {"tool": part.tool_name, "args": _short(part.args)}
                order.append(tool_id)
            elif kind == "ToolReturnPart":
                tool_id = getattr(part, "tool_call_id", None)
                entry = calls.get(tool_id)
                if entry is not None:
                    entry["result"] = _short(getattr(part, "content", None))
    return [calls[i] for i in order]


def append_entry(
    user_message: str,
    tool_calls: list[dict],
    stop_reason: str,
    user_id: int | None = None,
) -> None:
    """Append one record to the audit trail, creating the file if needed."""
    entry = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "user_id": user_id,
        "message": _short(user_message),
        "tools": tool_calls,
        "stop_reason": stop_reason,
    }

    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    trail: list = []
    if AUDIT_PATH.exists():
        try:
            trail = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
            if not isinstance(trail, list):
                trail = []
        except (json.JSONDecodeError, OSError):
            trail = []  # never crash a chat turn over the trail

    trail.append(entry)
    AUDIT_PATH.write_text(json.dumps(trail, indent=2), encoding="utf-8")
