# Architecture

## Overview

OpenClaw is a local-first, persona-driven AI assistant built on a deterministic, layered architecture. Every component is designed for auditability, reproducibility, and controlled-force execution.

## Directory Structure

```
openclaw/
├── main.py                   # Entry point (CLI + Web)
├── requirements.txt
├── openclaw.spec             # PyInstaller Windows .exe build
├── openclaw/
│   ├── config.py             # Central configuration (env vars)
│   ├── personas/             # Persona constraint engines
│   │   ├── base.py           # Persona dataclass
│   │   ├── shennell.py       # Zero-boundary persona
│   │   ├── analyst.py        # Structured analyst persona
│   │   └── builder.py        # Practical builder persona
│   ├── ai/
│   │   ├── memory.py         # Conversation memory with trimming
│   │   ├── tools.py          # All built-in tools + schemas
│   │   ├── agent.py          # Core persona-aware ReAct agent
│   │   ├── orchestrator.py   # Multi-agent routing
│   │   └── backends/
│   │       ├── base.py       # Abstract Backend interface
│   │       ├── openai_backend.py  # OpenAI / compatible API
│   │       └── local_backend.py   # Rule-based offline backend
│   ├── control/
│   │   ├── surface.py        # ControlSurface — all subsystem toggles
│   │   └── safety.py         # SafetyGate — hard rules
│   ├── cli/
│   │   └── interface.py      # Rich terminal interface
│   └── web/
│       ├── app.py            # Flask local web server
│       ├── templates/        # HTML (single-page app)
│       └── static/           # CSS + JavaScript
└── tests/
    ├── test_memory.py
    ├── test_tools.py
    ├── test_personas.py
    ├── test_control.py
    ├── test_agent.py
    └── test_main_smoke.py
```

## Agent Loop (ReAct)

```
User Input
    │
    ▼
System Prompt (persona)
    │
    ▼
Backend.complete(messages, tools)
    │
    ├─ Tool calls? ──► execute_tool() ──► SafetyGate.check() ──► ControlSurface.skill_allowed()
    │        └─────────────────────────────────────────────────► append result, loop
    │
    └─ Text response ──► return to user
```

## Control Surface Layers

```
ControlSurface (persisted to ~/.openclaw/control_surface.json)
├── PersonaControls   — enforcement, boundary strictness, speculation block
├── AgentControls     — per-agent enable/disable, auto-routing, timeout
├── SkillControls     — per-skill enable/disable
├── DeterminismControls — mode (strict/balanced/sandbox), hash locking
├── EvidenceControls  — safe mode, chain-of-custody, metadata extraction
├── LoggingControls   — mode (judicial/standard/minimal), export
└── ExecutionControls — step-through, developer mode, sandbox
```

## Safety Architecture

Hard rules enforced by `SafetyGate` — cannot be overridden by any control surface setting:

1. No self-modifying code
2. No unlogged transformations
3. No silent failures
4. No evidence destruction
5. No network access without explicit consent

## Multi-Agent Orchestration

The `Orchestrator` routes requests to the most appropriate agent based on content patterns:

- Legal/evidence keywords → Shennell
- Build/code keywords → Builder
- Analysis/comparison keywords → Analyst
- Default → Shennell

Each agent maintains its own conversation history. Agents are created lazily and cached.

## Web UI Architecture

```
Browser ──► Flask (127.0.0.1 only)
              ├── /             → Control surface SPA
              ├── /api/chat     → Agent chat
              ├── /api/control  → GET/POST control surface settings
              ├── /api/personas → Persona registry
              ├── /api/skills   → Skill list + enable status
              ├── /api/safety/rules → Hard rules display
              ├── /api/evidence → Evidence index
              ├── /api/chronology → Timeline
              └── /api/logs     → In-memory log buffer
```

## Evidence Pipeline

```
File input
    │
    ▼
SHA-256 hash (pre-modification)
    │
    ▼
Chain-of-custody entry (id, path, hash, size, timestamp)
    │
    ▼
Write to ~/.openclaw/evidence/index.json
    │
    ▼
(Never modify original file)
```
