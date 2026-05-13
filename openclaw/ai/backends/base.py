"""Abstract backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BackendResponse:
    """Normalised response from any backend."""

    def __init__(
        self,
        content: Optional[str],
        tool_calls: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.content = content
        self.tool_calls: List[Dict[str, Any]] = tool_calls or []

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class Backend(ABC):
    """Abstract base class for AI backends."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable backend name."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this backend is configured and reachable."""

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict]] = None,
    ) -> BackendResponse:
        """Send messages to the model and return a response."""
