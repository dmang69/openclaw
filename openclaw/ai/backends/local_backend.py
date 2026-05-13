"""Local rule-based backend — no external API required.

Understands basic intents (math, time, notes, evidence) by pattern-matching
the user message and routing to the appropriate tool. Responses are persona-aware.
"""

from __future__ import annotations

import ast as _ast
import re
from typing import Any, Dict, List, Optional, Tuple

from .base import Backend, BackendResponse


_GREETINGS = re.compile(r"\b(hi|hello|hey|howdy|greetings)\b", re.I)
_THANKS = re.compile(r"\b(thanks|thank you|thx|ty)\b", re.I)
_BYE = re.compile(r"\b(bye|goodbye|see you|exit|quit)\b", re.I)
_HELP_Q = re.compile(r"\b(help|what can you do|capabilities|commands)\b", re.I)
_ABOUT_Q = re.compile(r"\b(who are you|what are you|about you)\b", re.I)
_CALC_Q = re.compile(
    r"(calculate|compute|what is|what'?s|solve|eval|=\s*\?)\s+(.+)", re.I
)
_TIME_Q = re.compile(r"\b(time|date|day|today|now|current time|current date)\b", re.I)
_NOTE_LIST = re.compile(r"(list|show|view)\s+(my\s+)?notes?", re.I)
_NOTE_READ = re.compile(r"(read|open|show)\s+(?:my\s+)?note\s+(.+)", re.I)
_NOTE_SAVE = re.compile(r"(save|create|write|add)\s+(a\s+)?note", re.I)
_EVIDENCE_LIST = re.compile(r"(list|show)\s+(my\s+)?evidence", re.I)
_CHRONOLOGY_LIST = re.compile(r"(list|show|view)\s+(my\s+)?chronolog", re.I)


def _detect_tool_call(text: str) -> Tuple[Optional[str], Optional[Dict]]:
    """Return (tool_name, args) or (None, None)."""
    # Calculator via explicit keywords
    m = _CALC_Q.search(text)
    if m:
        expr = m.group(2).strip().rstrip("?.")
        return "calculator", {"expression": expr}

    # Pure math expression
    stripped = text.strip().rstrip("?=")
    try:
        _ast.parse(stripped, mode="eval")
        if re.search(r"[\d\+\-\*/]", stripped):
            return "calculator", {"expression": stripped}
    except Exception:
        pass

    # Date/time
    if _TIME_Q.search(text):
        return "get_datetime", {}

    # Note listing
    if _NOTE_LIST.search(text):
        return "list_notes", {}

    # Note reading
    m = _NOTE_READ.search(text)
    if m:
        return "read_note", {"title": m.group(2).strip()}

    # Evidence listing
    if _EVIDENCE_LIST.search(text):
        return "list_evidence", {}

    # Chronology listing
    if _CHRONOLOGY_LIST.search(text):
        return "list_chronology", {}

    return None, None


class LocalBackend(Backend):
    """Rule-based backend that works without any API key."""

    def __init__(self, persona_name: str = "shennell") -> None:
        self._persona_name = persona_name

    @property
    def name(self) -> str:
        return f"Local (rule-based, persona={self._persona_name})"

    def is_available(self) -> bool:
        return True

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict]] = None,
    ) -> BackendResponse:
        user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_msg = m.get("content") or ""
                break

        if tools:
            tool_name, tool_args = _detect_tool_call(user_msg)
            if tool_name:
                return BackendResponse(
                    content=None,
                    tool_calls=[
                        {"id": "local-0", "name": tool_name, "arguments": tool_args}
                    ],
                )

        return BackendResponse(content=self._respond(user_msg), tool_calls=[])

    def _respond(self, text: str) -> str:
        if _GREETINGS.search(text):
            return (
                f"Hello. I am OpenClaw ({self._persona_name} persona). "
                "I can calculate, check the time, manage notes, hash files, "
                "index evidence, and record chronological events. "
                "For full conversational AI, set OPENCLAW_API_KEY."
            )
        if _THANKS.search(text):
            return "Acknowledged. What else do you need?"
        if _BYE.search(text):
            return "Session ended."
        if _HELP_Q.search(text):
            return (
                "Available capabilities:\n"
                "  • Math calculations    — e.g. 'calculate 15% of 200'\n"
                "  • Date and time        — e.g. 'what time is it?'\n"
                "  • Notes               — save, list, and read notes\n"
                "  • File hashing        — SHA-256 integrity check\n"
                "  • Evidence indexing   — chain-of-custody file intake\n"
                "  • Chronology          — record and view timeline events\n\n"
                "Set OPENCLAW_API_KEY to enable full LLM-powered responses.\n"
                "CLI commands: /persona, /reset, /history, /backend, /help, /exit"
            )
        if _ABOUT_Q.search(text):
            return (
                "I am OpenClaw — an open-source AI assistant. "
                f"Active persona: {self._persona_name}. "
                "Running in local mode (no API key). "
                "Set OPENCLAW_API_KEY to unlock full AI capabilities."
            )
        return (
            "I am in local mode with limited capability. "
            "Try: 'calculate …', 'what time is it?', 'list notes', "
            "'list evidence', or 'list chronology'. "
            "Set OPENCLAW_API_KEY for full AI responses."
        )
