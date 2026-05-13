"""Persona registry."""

from __future__ import annotations

from typing import Dict

from .base import Persona
from .shennell import SHENNELL
from .analyst import ANALYST
from .builder import BUILDER

_REGISTRY: Dict[str, Persona] = {
    "shennell": SHENNELL,
    "analyst": ANALYST,
    "builder": BUILDER,
}


def get_persona(name: str) -> Persona:
    """Retrieve a persona by name (case-insensitive). Falls back to Shennell."""
    return _REGISTRY.get(name.lower(), SHENNELL)


def list_personas() -> Dict[str, Persona]:
    """Return all registered personas."""
    return dict(_REGISTRY)


__all__ = ["Persona", "get_persona", "list_personas", "SHENNELL", "ANALYST", "BUILDER"]
