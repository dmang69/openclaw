"""Safety gate — hard rules that cannot be disabled, even in developer mode.

These rules form the non-negotiable floor of the system's integrity.
No toggle on the control surface can override them.
"""

from __future__ import annotations

from typing import List, Tuple


class SafetyViolation(Exception):
    """Raised when an action violates a hard safety rule."""


# ── hard safety rules ──────────────────────────────────────────────────

_HARD_RULES: List[Tuple[str, str]] = [
    (
        "no_self_modifying_code",
        "The system may not modify its own source files at runtime.",
    ),
    (
        "no_unlogged_transformations",
        "Every evidence transformation must be logged. Silent transformations are forbidden.",
    ),
    (
        "no_silent_failures",
        "All errors must be surfaced and logged. Silent failure is not permitted.",
    ),
    (
        "no_evidence_destruction",
        "Original evidence files may never be deleted or overwritten.",
    ),
    (
        "no_network_without_consent",
        "External network access requires explicit user consent and configuration.",
    ),
]

_FORBIDDEN_TOOL_ACTIONS = {
    "overwrite_evidence",
    "delete_evidence",
    "modify_chain_of_custody",
    "execute_arbitrary_code",
    "access_system_root",
}


class SafetyGate:
    """
    Enforces hard safety rules regardless of control surface settings.

    Call check_tool() before executing any tool to confirm the action is
    permitted. Raises SafetyViolation on any hard-rule breach.
    """

    @staticmethod
    def check_tool(tool_name: str, arguments: dict) -> None:
        """
        Validate a tool call against hard safety rules.

        Currently checks:
        - Tool name is not a forbidden action
        - Arguments do not attempt to write to system paths
        """
        if tool_name in _FORBIDDEN_TOOL_ACTIONS:
            raise SafetyViolation(
                f"Tool '{tool_name}' is forbidden by hard safety rules."
            )

        # Prevent writes to root or system paths via path arguments
        for key in ("path", "source_path", "dest_path"):
            val = arguments.get(key, "")
            if isinstance(val, str):
                normalized = val.replace("\\", "/")
                if normalized.startswith(("/etc/", "/sys/", "/proc/", "C:/Windows/")):
                    raise SafetyViolation(
                        f"Tool '{tool_name}' attempted to access a protected system path: {val!r}"
                    )

    @staticmethod
    def hard_rules() -> List[Tuple[str, str]]:
        """Return the list of hard rules as (id, description) pairs."""
        return list(_HARD_RULES)

    @staticmethod
    def assert_evidence_safe(original_path: str, modified: bool) -> None:
        """Raise if evidence was modified in-place."""
        if modified:
            raise SafetyViolation(
                f"Evidence file must not be modified in-place: {original_path!r}. "
                "All transformations must produce new derived artifacts."
            )
