"""Persona base class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Persona:
    """A constraint engine that shapes agent behavior and identity."""

    name: str
    role: str
    voice: str
    system_prompt_addition: str
    hard_boundaries: List[str] = field(default_factory=list)
    forbidden_actions: List[str] = field(default_factory=list)
    error_posture: Dict[str, str] = field(default_factory=dict)

    def allows_action(self, action: str) -> bool:
        """Return True if this persona permits the given action."""
        return action.lower() not in [f.lower() for f in self.forbidden_actions]

    def boundary_message(self, situation: str) -> str:
        """Return the appropriate refusal message for a situation."""
        return self.error_posture.get(situation, self.error_posture.get("default", "I cannot proceed with that request."))

    def get_system_prompt(self) -> str:
        """Build the persona-specific addition to the system prompt."""
        lines = [self.system_prompt_addition]
        if self.hard_boundaries:
            lines.append("\nHard constraints you must always follow:")
            for b in self.hard_boundaries:
                lines.append(f"- {b}")
        return "\n".join(lines)
