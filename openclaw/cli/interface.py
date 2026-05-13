"""Interactive CLI for OpenClaw."""

from __future__ import annotations

import sys
from typing import Optional

from ..ai.orchestrator import Orchestrator
from ..personas import list_personas

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table

    _RICH = True
except ImportError:
    _RICH = False

_BANNER = r"""
   ___                  ____ _
  / _ \ _ __   ___ _ _ / ___| | __ ___      __
 | | | | '_ \ / _ \ '_ \___ \ |/ _` \ \ /\ / /
 | |_| | |_) |  __/ | | |__) | | (_| |\ V  V /
  \___/| .__/ \___|_| |_|____/|_|\__,_| \_/\_/
       |_|
"""

_COMMANDS = {
    "/help": "Show this help",
    "/persona <name>": "Switch persona (shennell | analyst | builder)",
    "/personas": "List all available personas",
    "/reset": "Clear conversation history",
    "/history": "Show conversation history",
    "/backend": "Show active AI backend",
    "/auto": "Enable automatic persona routing",
    "/exit": "Exit OpenClaw",
}


def _print_banner(console: Optional[object]) -> None:
    if _RICH and console:
        console.print(_BANNER, style="bold cyan")  # type: ignore[union-attr]
        console.print("  OpenClaw AI — open-source, persona-driven assistant\n", style="dim")  # type: ignore[union-attr]
    else:
        print(_BANNER)
        print("  OpenClaw AI — open-source, persona-driven assistant\n")


def _print_help(console: Optional[object]) -> None:
    if _RICH and console:
        table = Table(title="Commands", show_header=True, header_style="bold blue")
        table.add_column("Command", style="cyan")
        table.add_column("Description")
        for cmd, desc in _COMMANDS.items():
            table.add_row(cmd, desc)
        console.print(table)  # type: ignore[union-attr]
    else:
        print("Commands:")
        for cmd, desc in _COMMANDS.items():
            print(f"  {cmd:<30} {desc}")


def _print_personas(console: Optional[object]) -> None:
    personas = list_personas()
    if _RICH and console:
        table = Table(title="Available Personas", show_header=True, header_style="bold blue")
        table.add_column("Name", style="cyan")
        table.add_column("Role")
        table.add_column("Voice")
        for name, p in personas.items():
            table.add_row(name, p.role, p.voice)
        console.print(table)  # type: ignore[union-attr]
    else:
        print("Available personas:")
        for name, p in personas.items():
            print(f"  {name:<12} {p.role}")


def _print_response(text: str, console: Optional[object]) -> None:
    if _RICH and console:
        try:
            console.print(Markdown(text))  # type: ignore[union-attr]
        except Exception:
            console.print(text)  # type: ignore[union-attr]
    else:
        print(f"\nOpenClaw: {text}\n")


def _info(msg: str, console: Optional[object]) -> None:
    if _RICH and console:
        console.print(f"[dim]{msg}[/dim]")  # type: ignore[union-attr]
    else:
        print(msg)


def _error(msg: str, console: Optional[object]) -> None:
    if _RICH and console:
        console.print(f"[bold red]{msg}[/bold red]")  # type: ignore[union-attr]
    else:
        print(f"ERROR: {msg}", file=sys.stderr)


def run_cli() -> None:
    """Start the interactive CLI session."""
    console = Console() if _RICH else None
    orch = Orchestrator()

    # Start with Shennell agent as default
    current_agent = orch.agent("shennell")
    auto_route = False

    _print_banner(console)

    if _RICH and console:
        console.print(
            f"Persona: [bold green]{current_agent.persona.name}[/bold green]  "
            f"Backend: [bold yellow]{current_agent.backend_name}[/bold yellow]\n"
        )
        console.print(
            "Type a message or [bold]/help[/bold] for commands. "
            "[bold]/exit[/bold] to quit.\n"
        )
    else:
        print(f"Persona: {current_agent.persona.name}  Backend: {current_agent.backend_name}\n")
        print("Type a message or /help for commands. /exit to quit.\n")

    while True:
        try:
            if _RICH and console:
                user_input = Prompt.ask(
                    f"[bold blue]You[/bold blue] "
                    f"[dim]({current_agent.persona.name})[/dim]"
                )
            else:
                user_input = input(f"You ({current_agent.persona.name}): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        cmd = user_input.strip()
        lower = cmd.lower()

        if lower in ("/exit", "/quit"):
            print("Goodbye!")
            break

        if lower == "/help":
            _print_help(console)
            continue

        if lower == "/personas":
            _print_personas(console)
            continue

        if lower == "/reset":
            current_agent.reset()
            _info("Conversation history cleared.", console)
            continue

        if lower == "/history":
            history = current_agent.history()
            if not history:
                _info("No history yet.", console)
            else:
                for m in history:
                    role = m.get("role", "?")
                    content = (m.get("content") or "")[:300]
                    if _RICH and console:
                        console.print(f"[bold]{role}:[/bold] {content}")  # type: ignore[union-attr]
                    else:
                        print(f"{role}: {content}")
            continue

        if lower == "/backend":
            _info(f"Active backend: {current_agent.backend_name}", console)
            continue

        if lower == "/auto":
            auto_route = not auto_route
            state = "enabled" if auto_route else "disabled"
            _info(f"Automatic persona routing {state}.", console)
            continue

        if lower.startswith("/persona "):
            persona_name = cmd[9:].strip()
            try:
                current_agent = orch.agent(persona_name)
                auto_route = False
                _info(
                    f"Switched to {current_agent.persona.name} persona "
                    f"({current_agent.persona.role}).",
                    console,
                )
            except Exception as exc:
                _error(f"Cannot switch persona: {exc}", console)
            continue

        # Regular chat
        try:
            if auto_route:
                # Let the orchestrator pick the best agent
                agent_to_use = orch.route(user_input)
                if agent_to_use is not current_agent:
                    _info(
                        f"[auto-routed → {agent_to_use.persona.name}]",
                        console,
                    )
            else:
                agent_to_use = current_agent

            if _RICH and console:
                with console.status("[dim]Thinking…[/dim]", spinner="dots"):  # type: ignore[union-attr]
                    response = agent_to_use.chat(user_input)
            else:
                response = agent_to_use.chat(user_input)

            if _RICH and console:
                console.print(f"\n[bold green]{agent_to_use.persona.name}:[/bold green]")  # type: ignore[union-attr]
            _print_response(response, console)

        except KeyboardInterrupt:
            print("\n[Interrupted]")
        except Exception as exc:
            _error(f"Error: {exc}", console)
