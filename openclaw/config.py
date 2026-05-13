"""Central configuration — loaded from environment variables."""

import os


class Config:
    # Backend: "auto", "openai", "local"
    BACKEND: str = os.environ.get("OPENCLAW_BACKEND", "auto")

    # OpenAI / OpenAI-compatible API
    API_KEY: str = os.environ.get("OPENCLAW_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    API_BASE: str = os.environ.get("OPENCLAW_API_BASE", "https://api.openai.com/v1")
    MODEL: str = os.environ.get("OPENCLAW_MODEL", "gpt-4o-mini")

    # Agent settings
    MAX_ITERATIONS: int = int(os.environ.get("OPENCLAW_MAX_ITERATIONS", "10"))
    MAX_MEMORY_MESSAGES: int = int(os.environ.get("OPENCLAW_MAX_MEMORY_MESSAGES", "50"))
    TEMPERATURE: float = float(os.environ.get("OPENCLAW_TEMPERATURE", "0.7"))

    # Active persona: "shennell", "analyst", "builder"
    PERSONA: str = os.environ.get("OPENCLAW_PERSONA", "shennell")

    # Storage directories
    NOTES_DIR: str = os.environ.get(
        "OPENCLAW_NOTES_DIR",
        os.path.join(os.path.expanduser("~"), ".openclaw", "notes"),
    )
    EVIDENCE_DIR: str = os.environ.get(
        "OPENCLAW_EVIDENCE_DIR",
        os.path.join(os.path.expanduser("~"), ".openclaw", "evidence"),
    )
    CHRONOLOGY_DIR: str = os.environ.get(
        "OPENCLAW_CHRONOLOGY_DIR",
        os.path.join(os.path.expanduser("~"), ".openclaw", "chronology"),
    )
