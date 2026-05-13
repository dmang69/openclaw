# openclaw

## Project Title

A deterministic, local-first system engineered for precision, auditability, and controlled force.

## Overview

This repository provides a modular, persona-driven automation system designed for environments where clarity, reproducibility, and evidentiary integrity are non-negotiable. The architecture emphasizes deterministic execution, transparent state transitions, and strict separation between configuration, logic, and record.

## Features

- Local-first execution (no cloud dependency unless explicitly configured)
- Deterministic agent loops with reproducible outputs
- Persona-driven architecture (e.g., Shennell: Zero-Boundary)
- Modular skills, tools, and adapters
- Audit-ready logs and chronological traceability
- Optional Windows 11 `.exe` installer
- Evidence-indexed reasoning (if enabled)

## Installation (Windows 11)

A Windows-ready `.exe` installer is available for users who require a clean, offline-capable execution environment.

1. Go to the Releases page.
2. Download the latest `.exe` installer.
3. Run the installer and follow the prompts.
4. Launch the application from the Start Menu or desktop shortcut.
5. The system initializes with local configuration, persona files, and agent modules pre-loaded.

## Running the Application

After installation:

- Launch the application normally.
- The system loads its persona, skills, and configuration.
- Logs are written to the local `logs/` directory.
- All state transitions are deterministic and traceable.

## Configuration

Configuration files are stored in:

```text
config/
  personas/
  ui_settings.json
  system.json
```

Modify these files to adjust behavior, enable or disable agents, or extend capabilities.

## Development

To run from source:

```bash
pip install -r requirements.txt
python main.py
```

## Building the Windows `.exe`

A GitHub Actions workflow automatically builds the `.exe` on tagged releases.

Manual build:

```bash
pyinstaller --onefile --noconsole main.py
```

## Windows Installer UI Text Set

Installer dialog copy is maintained at:

- `installer/windows/INSTALLER_UI_TEXT.md`

## Shennell First-Run Message

First-run launch message content is stored at:

- `config/personas/shennell_first_run_message.txt`

## Architecture

Full system design, usage, operations reference, and architecture diagrams (including multi-agent orchestration, evidence/chronology expansion, productization layer, documentation site buildout, and the deterministic execution contract) are in [ARCHITECTURE.md](ARCHITECTURE.md).

## Developer Guide

Contributor reference for environment setup, coding standards, testing, system extension, and full API reference: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).

## License

MIT License.  
You may use, modify, and distribute this project with attribution.
# OpenClaw

**Open-source, local-first AI assistant with persona-driven control surface.**

```
   ___                  ____ _
  / _ \ _ __   ___ _ _ / ___| | __ ___      __
 | | | | '_ \ / _ \ '_ \___ \ |/ _` \ \ /\ / /
 | |_| | |_) |  __/ | | |__) | | (_| |\ V  V /
  \___/| .__/ \___|_| |_|____/|_|\__,_| \_/\_/
       |_|
```

## Features

| Feature | Description |
|---|---|
| **Multi-persona system** | Shennell (zero-boundary), Analyst (structured), Builder (practical) |
| **Multi-agent orchestration** | Automatic routing to the best agent per request |
| **Tool use** | Calculator, datetime, notes, file hashing, evidence indexing, chronology |
| **Evidence pipeline** | SHA-256 chain-of-custody indexing — never modifies originals |
| **Control Surface** | Per-subsystem toggles: personas, agents, skills, determinism, evidence, logging |
| **Safety gate** | Hard rules that cannot be disabled — no evidence destruction, no silent failures |
| **Web UI** | Professional dark-mode control surface served on localhost |
| **CLI** | Rich terminal interface with persona switching |
| **Windows .exe** | PyInstaller + GitHub Actions automated release builds |

## Quick Start

### Requirements

- Python 3.10+
- `pip install -r requirements.txt`

### CLI Mode (default)

```bash
python main.py
```

### Web UI Mode

```bash
python main.py --web
# Opens http://127.0.0.1:5000 automatically
```

### With OpenAI API

```bash
export OPENCLAW_API_KEY=sk-...
python main.py
```

### With OpenAI-compatible local server (Ollama, LM Studio)

```bash
export OPENCLAW_API_KEY=any
export OPENCLAW_API_BASE=http://localhost:11434/v1
export OPENCLAW_MODEL=llama3
python main.py
```

## Configuration

All settings via environment variables:

| Variable | Default | Description |
|---|---|---|
| `OPENCLAW_API_KEY` | — | OpenAI API key (optional) |
| `OPENCLAW_API_BASE` | `https://api.openai.com/v1` | API base URL |
| `OPENCLAW_MODEL` | `gpt-4o-mini` | Model name |
| `OPENCLAW_BACKEND` | `auto` | `auto`, `openai`, or `local` |
| `OPENCLAW_PERSONA` | `shennell` | Default persona |
| `OPENCLAW_TEMPERATURE` | `0.7` | Model temperature |

Control surface settings persist to `~/.openclaw/control_surface.json`.

## Personas

| Persona | Role | Voice |
|---|---|---|
| **Shennell** | Zero-boundary architect | Precise, disciplined, non-speculative |
| **Analyst** | Structured analyst | Structured, explanatory, neutral |
| **Builder** | Implementation engineer | Practical, direct, solution-oriented |

## CLI Commands

| Command | Description |
|---|---|
| `/help` | Show all commands |
| `/persona <name>` | Switch persona |
| `/personas` | List available personas |
| `/reset` | Clear conversation history |
| `/history` | Show conversation history |
| `/backend` | Show active AI backend |
| `/auto` | Toggle automatic persona routing |
| `/exit` | Exit |

## Web UI Tabs

| Tab | Description |
|---|---|
| **Chat** | Conversational interface with persona selector |
| **Control Surface** | Toggle every subsystem — Simple Mode + Advanced Mode |
| **Evidence** | View indexed evidence index |
| **Chronology** | View recorded event timeline |
| **Logs** | Real-time system log stream |
| **Safety** | Hard safety rules that can never be disabled |

## Windows .exe

A release build is available on the [Releases](../../releases) page.

Manual build:
```bash
pip install pyinstaller
pyinstaller openclaw.spec
# Output: dist/openclaw.exe
```

## Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full architecture reference including agent loop, control surface layers, safety architecture, multi-agent orchestration, web UI structure, and evidence pipeline.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — free to use, modify, and distribute with attribution.
