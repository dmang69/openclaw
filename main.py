#!/usr/bin/env python3
"""Deterministic local-first entrypoint for openclaw."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONFIG_DIR = ROOT / "config"
LOGS_DIR = ROOT / "logs"


@dataclass(frozen=True)
class SessionContext:
    agent: str
    persona: str
    log_mode: str
    dev_mode: bool
    config_path: str
    started_at_utc: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="m13thco-agent",
        description="Run the deterministic local-first openclaw application.",
    )
    parser.add_argument("--agent", default="strategist", help="Agent name to run.")
    parser.add_argument(
        "--persona",
        default="shennell",
        help="Persona name to use (default: shennell).",
    )
    parser.add_argument(
        "--log",
        dest="log_mode",
        choices=("judicial", "standard", "minimal"),
        default="judicial",
        help="Logging mode.",
    )
    parser.add_argument(
        "--config",
        default=str(CONFIG_DIR / "system.json"),
        help="Path to runtime config file.",
    )
    parser.add_argument("--dev", action="store_true", help="Enable development mode.")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_persona_message(persona: str) -> str:
    message_file = CONFIG_DIR / "personas" / f"{persona.lower()}_first_run_message.txt"
    if message_file.exists():
        return message_file.read_text(encoding="utf-8").strip()
    return (
        f"Persona '{persona}' is active. Constraint-first deterministic mode engaged."
    )


def build_context(args: argparse.Namespace) -> SessionContext:
    return SessionContext(
        agent=args.agent,
        persona=args.persona,
        log_mode=args.log_mode,
        dev_mode=args.dev,
        config_path=str(Path(args.config).resolve()),
        started_at_utc=datetime.now(timezone.utc).isoformat(),
    )


def write_session_log(context: SessionContext, system_config: dict[str, Any]) -> Path:
    LOGS_DIR.mkdir(exist_ok=True)
    timestamp = (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace(":", "-")
        .replace("+00:00", "Z")
    )
    log_file = LOGS_DIR / f"session-{timestamp}.jsonl"
    event = {
        "event": "session_start",
        "context": asdict(context),
        "system_config": system_config,
    }
    log_file.write_text(json.dumps(event, sort_keys=True) + "\n", encoding="utf-8")
    return log_file


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    system_config = read_json(config_path)
    context = build_context(args)
    persona_message = read_persona_message(args.persona)
    log_file = write_session_log(context, system_config)

    print("openclaw started")
    print(f"agent={context.agent}")
    print(f"persona={context.persona}")
    print(f"log_mode={context.log_mode}")
    print(f"dev_mode={str(context.dev_mode).lower()}")
    print(f"config={context.config_path}")
    print(f"log_file={log_file}")
    print("")
    print(persona_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
