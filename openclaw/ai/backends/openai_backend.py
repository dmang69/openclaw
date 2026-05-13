"""OpenAI and OpenAI-compatible API backend."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .base import Backend, BackendResponse
from ...config import Config


class OpenAIBackend(Backend):
    """Backend for OpenAI or any OpenAI-compatible API (Ollama, LM Studio, etc.)."""

    def __init__(self) -> None:
        # Lazy import so the module loads even if openai is not installed
        import openai

        self._client = openai.OpenAI(
            api_key=Config.API_KEY or "no-key",
            base_url=Config.API_BASE,
        )
        self._model = Config.MODEL

    @property
    def name(self) -> str:
        return f"OpenAI ({self._model})"

    def is_available(self) -> bool:
        return bool(Config.API_KEY)

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict]] = None,
    ) -> BackendResponse:
        params: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": Config.TEMPERATURE,
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        response = self._client.chat.completions.create(**params)
        msg = response.choices[0].message

        tool_calls: List[Dict[str, Any]] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments),
                    }
                )

        return BackendResponse(content=msg.content, tool_calls=tool_calls)
