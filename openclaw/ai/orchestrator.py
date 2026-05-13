"""Multi-agent orchestrator — routes requests to the most appropriate agent.

The orchestrator maintains a pool of named agents, each with a specific
persona, and selects the best one based on the request content.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from ..personas import list_personas
from .agent import Agent

# ── intent patterns ────────────────────────────────────────────────────

_LEGAL_PATTERNS = re.compile(
    r"\b(evidence|legal|court|tribunal|chronol|affidavit|exhibit|"
    r"procedur|petition|disclose|discovery|chain.of.custody|judicial)\b",
    re.I,
)
_ANALYSIS_PATTERNS = re.compile(
    r"\b(analys|compare|evaluate|assess|review|summar|explain|break.?down)\b",
    re.I,
)
_BUILD_PATTERNS = re.compile(
    r"\b(build|create|implement|code|write code|generate|script|function|class)\b",
    re.I,
)


class Orchestrator:
    """
    Routes user requests to the best-suited agent.

    Agents are created lazily and cached.  The default agent is 'shennell'.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}
        self._default = "shennell"

    # ── public API ─────────────────────────────────────────────────────

    def agent(self, persona_name: str) -> Agent:
        """Get (or create) the agent for a given persona."""
        name = persona_name.lower()
        if name not in self._agents:
            self._agents[name] = Agent()
            self._agents[name].set_persona(name)
        return self._agents[name]

    def route(self, user_input: str) -> Agent:
        """Select the most appropriate agent for the given input."""
        if _LEGAL_PATTERNS.search(user_input):
            return self.agent("shennell")
        if _BUILD_PATTERNS.search(user_input):
            return self.agent("builder")
        if _ANALYSIS_PATTERNS.search(user_input):
            return self.agent("analyst")
        return self.agent(self._default)

    def chat(self, user_input: str, persona_override: Optional[str] = None) -> str:
        """
        Route a message, optionally overriding the agent selection, and return
        the response.
        """
        if persona_override:
            ag = self.agent(persona_override)
        else:
            ag = self.route(user_input)
        return ag.chat(user_input)

    def list_agents(self) -> List[str]:
        """Return names of all cached agents."""
        return list(self._agents.keys())

    def reset_all(self) -> None:
        """Clear all agent conversation histories."""
        for ag in self._agents.values():
            ag.reset()
