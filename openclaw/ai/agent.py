"""Core OpenClaw agent — persona-aware, tool-using, multi-turn conversation."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from ..config import Config
from ..personas import Persona, get_persona
from .backends.base import Backend, BackendResponse
from .backends.local_backend import LocalBackend
from .backends.openai_backend import OpenAIBackend
from .memory import ConversationMemory
from .tools import TOOL_SCHEMAS, execute_tool

logger = logging.getLogger(__name__)


def _make_backend(persona_name: str) -> Backend:
    """Select and instantiate the best available backend."""
    mode = Config.BACKEND.lower()
    if mode == "local":
        return LocalBackend(persona_name=persona_name)
    if mode in ("openai", "auto"):
        if Config.API_KEY:
            try:
                return OpenAIBackend()
            except ImportError:
                logger.warning("openai package not installed; falling back to local backend")
        return LocalBackend(persona_name=persona_name)
    return LocalBackend(persona_name=persona_name)


class Agent:
    """
    The OpenClaw agent.

    Accepts user messages, applies the active persona, uses tools as needed
    (via the ReAct loop), and returns a final response.
    """

    def __init__(
        self,
        backend: Optional[Backend] = None,
        persona: Optional[Persona] = None,
    ) -> None:
        self._persona: Persona = persona or get_persona(Config.PERSONA)
        self._backend: Backend = backend or _make_backend(self._persona.name.lower())
        self._memory = ConversationMemory(Config.MAX_MEMORY_MESSAGES)
        self._max_iterations = Config.MAX_ITERATIONS

    # ── public API ─────────────────────────────────────────────────────

    @property
    def persona(self) -> Persona:
        return self._persona

    @property
    def backend_name(self) -> str:
        return self._backend.name

    def set_persona(self, name: str) -> None:
        """Switch to a different persona (resets conversation context)."""
        self._persona = get_persona(name)
        self._memory.clear()
        # Rebuild backend so local backend uses the new persona name
        if isinstance(self._backend, LocalBackend):
            self._backend = LocalBackend(persona_name=self._persona.name.lower())

    def chat(self, user_input: str) -> str:
        """
        Process a user message and return the assistant response.

        Runs the ReAct loop: if the model calls tools, executes them and feeds
        results back until the model produces a final text response.
        """
        self._memory.add_user(user_input)

        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages.extend(self._memory.get_messages())

        response_text = ""

        for iteration in range(self._max_iterations):
            response: BackendResponse = self._backend.complete(messages, tools=TOOL_SCHEMAS)

            if response.has_tool_calls:
                # Append assistant turn with tool call declarations
                assistant_msg: Dict[str, Any] = {
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc["arguments"]),
                            },
                        }
                        for tc in response.tool_calls
                    ],
                }
                messages.append(assistant_msg)

                # Execute tools and append results
                for tc in response.tool_calls:
                    result = execute_tool(tc["name"], tc["arguments"])
                    logger.debug(
                        "Tool %s(%s) → %s", tc["name"], tc["arguments"], result[:200]
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "name": tc["name"],
                            "content": result,
                        }
                    )
            else:
                response_text = response.content or ""
                break

        self._memory.add_assistant(response_text)
        return response_text

    def reset(self) -> None:
        """Clear conversation history."""
        self._memory.clear()

    def history(self) -> List[Dict[str, Any]]:
        """Return the raw conversation history."""
        return self._memory.get_messages()

    # ── private ────────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        base = (
            f"You are OpenClaw, an AI assistant. "
            f"Active persona: {self._persona.name} ({self._persona.role}).\n\n"
            f"{self._persona.get_system_prompt()}"
        )
        return base
