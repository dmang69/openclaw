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
