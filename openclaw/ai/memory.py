"""Conversation memory management."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ConversationMemory:
    """Manages conversation history with automatic trimming."""

    def __init__(self, max_messages: int = 50) -> None:
        self.max_messages = max_messages
        self._messages: List[Dict[str, Any]] = []

    def add_user(self, content: str) -> None:
        self._messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content: str, tool_calls: Optional[List] = None) -> None:
        msg: Dict[str, Any] = {"role": "assistant", "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self._messages.append(msg)

    def add_tool_result(self, tool_call_id: str, name: str, content: str) -> None:
        self._messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": name,
                "content": content,
            }
        )

    def get_messages(self) -> List[Dict[str, Any]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def _trim(self) -> None:
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages :]

    def __len__(self) -> int:
        return len(self._messages)
