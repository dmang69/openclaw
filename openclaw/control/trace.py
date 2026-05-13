"""Execution trace — records every step of an agent loop for the UI execution panel.

Events are kept in a bounded in-memory ring buffer and exposed via the web API.
Each event is a structured dict that the frontend can render in the execution panel.
"""

from __future__ import annotations

import datetime
import threading
from typing import Any, Dict, List, Optional

_MAX_EVENTS = 200
_buffer: List[Dict[str, Any]] = []
_lock = threading.Lock()


# ── event types ────────────────────────────────────────────────────────

AGENT_SELECTED = "agent_selected"
SKILL_CALLED = "skill_called"
SKILL_RESULT = "skill_result"
PERSONA_APPLIED = "persona_applied"
PERSONA_VIOLATION = "persona_violation"
RESPONSE_GENERATED = "response_generated"
LOOP_ITERATION = "loop_iteration"
SAFETY_CHECK = "safety_check"
CONTROL_CHANGE = "control_change"
ERROR = "error"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ── public API ─────────────────────────────────────────────────────────

def record(
    event_type: str,
    *,
    agent: str = "",
    persona: str = "",
    skill: Optional[str] = None,
    detail: str = "",
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Record a single trace event into the ring buffer."""
    event: Dict[str, Any] = {
        "timestamp": _now(),
        "event_type": event_type,
        "agent": agent,
        "persona": persona,
        "detail": detail,
    }
    if skill:
        event["skill"] = skill
    if data:
        event["data"] = data

    with _lock:
        _buffer.append(event)
        if len(_buffer) > _MAX_EVENTS:
            _buffer.pop(0)


def get_recent(n: int = 50) -> List[Dict[str, Any]]:
    """Return the most recent *n* trace events (oldest first)."""
    with _lock:
        return list(_buffer[-n:])


def clear() -> None:
    """Flush the trace buffer."""
    with _lock:
        _buffer.clear()


def get_active_summary() -> Dict[str, Any]:
    """
    Return a summary of the current execution state for the dashboard header.

    Walks back through the buffer to find the most recent agent selection,
    persona application, and skill call.
    """
    with _lock:
        recent = list(reversed(_buffer))

    summary: Dict[str, Any] = {
        "active_agent": None,
        "active_persona": None,
        "last_skill": None,
        "last_skill_at": None,
        "event_count": len(_buffer),
    }

    for event in recent:
        if summary["active_agent"] is None and event.get("agent"):
            summary["active_agent"] = event["agent"]
        if summary["active_persona"] is None and event.get("persona"):
            summary["active_persona"] = event["persona"]
        if summary["last_skill"] is None and event.get("skill"):
            summary["last_skill"] = event["skill"]
            summary["last_skill_at"] = event["timestamp"]
        if all(v is not None for v in (
            summary["active_agent"],
            summary["active_persona"],
            summary["last_skill"],
        )):
            break

    return summary
