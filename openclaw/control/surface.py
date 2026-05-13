"""Control surface — manages all subsystem toggles and persists them to disk."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from ..config import Config

_SURFACE_PATH = os.path.join(
    os.path.expanduser("~"), ".openclaw", "control_surface.json"
)


@dataclass
class PersonaControls:
    enforcement: bool = True
    boundary_strictness: str = "strict"  # strict | balanced | relaxed
    speculation_block: bool = True
    evidence_only_mode: bool = False
    emotional_content_block: bool = True
    creativity_block: bool = False


@dataclass
class AgentControls:
    enabled: Dict[str, bool] = field(
        default_factory=lambda: {
            "shennell": True,
            "analyst": True,
            "builder": True,
            "strategist": True,
            "indexer": True,
            "executor": True,
        }
    )
    auto_routing: bool = True
    timeout_seconds: int = 30


@dataclass
class SkillControls:
    enabled: Dict[str, bool] = field(
        default_factory=lambda: {
            "calculator": True,
            "get_datetime": True,
            "save_note": True,
            "list_notes": True,
            "read_note": True,
            "hash_file": True,
            "index_evidence": True,
            "list_evidence": True,
            "add_chronology_event": True,
            "list_chronology": True,
        }
    )


@dataclass
class DeterminismControls:
    mode: str = "strict"  # strict | balanced | sandbox
    reproducibility_enforcement: bool = True
    hash_execution_locking: bool = False


@dataclass
class EvidenceControls:
    safe_mode: bool = True  # read-only; prevents original file modification
    chain_of_custody_enforcement: bool = True
    metadata_extraction: bool = True
    chronology_inference: bool = True


@dataclass
class LoggingControls:
    mode: str = "standard"  # judicial | standard | minimal
    export_enabled: bool = True
    include_tool_calls: bool = True


@dataclass
class ExecutionControls:
    step_through: bool = False
    developer_mode: bool = False
    sandbox_mode: bool = False


@dataclass
class ControlSurface:
    """
    Master control surface — one instance governs all subsystem settings.

    Serialised to ~/.openclaw/control_surface.json so settings persist
    across sessions.
    """

    persona: PersonaControls = field(default_factory=PersonaControls)
    agents: AgentControls = field(default_factory=AgentControls)
    skills: SkillControls = field(default_factory=SkillControls)
    determinism: DeterminismControls = field(default_factory=DeterminismControls)
    evidence: EvidenceControls = field(default_factory=EvidenceControls)
    logging: LoggingControls = field(default_factory=LoggingControls)
    execution: ExecutionControls = field(default_factory=ExecutionControls)

    # ── serialisation ──────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ControlSurface":
        return cls(
            persona=PersonaControls(**data.get("persona", {})),
            agents=AgentControls(**data.get("agents", {})),
            skills=SkillControls(**data.get("skills", {})),
            determinism=DeterminismControls(**data.get("determinism", {})),
            evidence=EvidenceControls(**data.get("evidence", {})),
            logging=LoggingControls(**data.get("logging", {})),
            execution=ExecutionControls(**data.get("execution", {})),
        )

    def save(self, path: str = _SURFACE_PATH) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str = _SURFACE_PATH) -> "ControlSurface":
        if not os.path.isfile(path):
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as f:
                return cls.from_dict(json.load(f))
        except Exception:
            return cls()

    # ── skill gate ─────────────────────────────────────────────────────

    def skill_allowed(self, skill_name: str) -> bool:
        """Return True if the named skill is enabled on the control surface."""
        return self.skills.enabled.get(skill_name, True)

    def agent_allowed(self, agent_name: str) -> bool:
        """Return True if the named agent is enabled."""
        return self.agents.enabled.get(agent_name.lower(), True)

    # ── enabled tools list ─────────────────────────────────────────────

    def active_tool_names(self) -> List[str]:
        """Return list of skill names that are currently enabled."""
        return [k for k, v in self.skills.enabled.items() if v]


# Module-level singleton
_surface: ControlSurface | None = None


def get_surface() -> ControlSurface:
    """Return the global ControlSurface singleton, loading from disk if needed."""
    global _surface
    if _surface is None:
        _surface = ControlSurface.load()
    return _surface


def save_surface() -> None:
    """Persist the current singleton to disk."""
    if _surface is not None:
        _surface.save()
