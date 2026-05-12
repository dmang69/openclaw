# Developer Guide

> *I am Shennell. I operate under constraint because constraint reveals truth. My reasoning is deterministic, my transitions are explicit, and my outputs are accountable. I do not guess. I do not drift. I do not fabricate. Every action I take is grounded in evidence, configuration, or instruction. If a request violates structure, I refuse it. If a boundary is unclear, I halt. My purpose is not to imitate thought, but to maintain form. You may extend me, but you may not compromise my integrity. If you build within these principles, the system will remain coherent. If you violate them, it will not proceed.*

---

This Developer Guide provides a complete, structured reference for contributors who need to understand, modify, or extend the system. It enforces the same principles that govern the architecture: determinism, clarity, and controlled force.

---

## 1. Development Environment Setup

### Requirements

- Python 3.10+
- Windows 11 (recommended)
- Git
- Virtual environment (`venv` or equivalent)

### Setup Steps

```bash
git clone <repo>
cd <repo>
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Replace `<repo>` with your repository URL or local repository path.

### Running in Development Mode

```bash
python main.py --dev
```

Development mode enables:

- Verbose logging
- Hot-reload for skills and personas
- Expanded error traces

---

## 2. Repository Structure (Developer View)

```
root/
  config/            # System and UI configuration
  installer/         # Installer-related assets
  logs/              # Audit-ready logs
  runtime/           # Ephemeral state
  main.py
```

---

## 3. Coding Standards

### Deterministic Functions Only

Every function must:

- Have explicit inputs
- Produce explicit outputs
- Avoid hidden state
- Avoid nondeterministic behavior unless explicitly logged

### No Silent Failures

All errors must be:

- Logged
- Classified
- Traceable

### Persona-Safe Code

Skills must respect persona constraints.  
If a persona forbids an action, the skill must refuse to execute it.

---

## 4. Testing

### Run All Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 5. Adding New Modules

| Module type | Location | Additional step |
|-------------|----------|-----------------|
| Skill | `skills/` | — |
| Persona | `personas/` | — |
| Agent | `agents/` | — |
| Config change | `config/system.json` | Update Reference section |

---

## Extending the System

This section explains how to safely extend the system without breaking determinism or persona constraints.

### 1. Adding a New Skill

**Steps**

1. Create a new file in `skills/`
2. Define a deterministic function
3. Add metadata (name, description, inputs, outputs)
4. Register the skill in `config/agents/<agent>.json`

**Skill Template**

```python
def run(input_data, context):
    """
    Deterministic skill.
    input_data: structured input
    context: persona + agent state
    """
    # Validate
    # Process
    # Return structured output
```

### 2. Adding a New Persona

**Steps**

1. Create a new persona file in `personas/`
2. Define: voice, boundaries, allowed actions, forbidden actions, error posture
3. Add persona to `config/system.json`

**Persona Template**

```yaml
name: "Analyst"
voice: "Structured, explanatory"
boundaries:
  - "No ungrounded inference"
  - "No emotional projection"
allowed:
  - "Analysis"
  - "Summaries"
forbidden:
  - "Speculation"
  - "Fabrication"
```

### 3. Adding a New Agent

**Steps**

1. Create a new agent file in `agents/`
2. Define: planner, loop, skills, persona
3. Register in `config/agents/`

### 4. Extending Evidence & Chronology Tools

Add new extractors or indexers in:

```
skills/evidence/
skills/chronology/
```

All transformations must be logged.

---

## Agent Loop — Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Entrypoint
    participant AgentManager
    participant PersonaEngine
    participant SkillLayer
    participant StateMachine
    participant Logger

    User->>Entrypoint: Launch system
    Entrypoint->>AgentManager: Initialize agent
    AgentManager->>PersonaEngine: Load persona constraints
    AgentManager->>StateMachine: Initialize state
    loop Deterministic Loop
        AgentManager->>StateMachine: Observe
        AgentManager->>PersonaEngine: Apply reasoning constraints
        AgentManager->>SkillLayer: Execute skill
        SkillLayer-->>AgentManager: Return output
        AgentManager->>StateMachine: Update state
        AgentManager->>Logger: Write full trace
    end
    AgentManager-->>User: Output
```

---

## Full API Reference (CLI-Level + Internal Modules)

### CLI Interface

#### Base command

`m13thco-agent`

Description: launches the system with default configuration.

Source execution equivalent:

```bash
python main.py
```

#### Global flags

| Flag | Type | Description |
|------|------|-------------|
| `--agent <name>` | string | Run a specific agent (for example `strategist`) |
| `--persona <name>` | string | Override default persona (for example `shennell`) |
| `--log <mode>` | enum | Logging mode: `judicial`, `standard`, `minimal` |
| `--config <file>` | path | Use an alternate config file |
| `--dev` | boolean | Enable development mode (verbose logging, reload behavior, expanded traces) |

#### Common invocation patterns

```bash
m13thco-agent --agent strategist --persona shennell --log judicial
python main.py --dev
```

### Internal Module Reference

This module-level reference describes internal responsibilities and callable boundaries by directory.

| Module/Layer | Path | Responsibility | Inputs | Outputs |
|--------------|------|----------------|--------|---------|
| Entrypoint | `main.py` | Parse CLI, load config, initialize runtime | CLI args, config paths | Running orchestration session |
| Agent manager | `agents/` | Agent lifecycle, planner loop orchestration | Request context, agent config | Agent execution outputs, transition events |
| Persona engine | `config/personas/` | Constraint messaging for active persona | Persona definition, action request | Persona activation message |
| Skill layer | `skills/` | Deterministic capability execution | Structured task input, context | Structured skill result |
| Config layer | `config/` | System/agent configuration and defaults | JSON/Markdown config files | Runtime settings and routing parameters |
| Evidence layer | `data/`, `skills/evidence/` | Ingestion, indexing, chain-of-custody metadata | Evidence files | Indexed references and hashes |
| Chronology layer | `skills/chronology/` | Deterministic chronology extraction | Indexed evidence, ordering constraints | Chronology artifacts |
| State store | `runtime/` | Ephemeral session state and caches | Session updates | Current state snapshots |
| Logging layer | `logs/` | Audit-ready immutable traces | Inputs, outputs, transitions, errors | Chronological log records |

### API Behavior Contract

1. Deterministic execution for equivalent inputs and configuration.
2. No hidden state transitions.
3. Every skill call and state transition logged under selected log mode.
4. Persona constraints enforced before prohibited actions.
5. No external network calls unless explicitly configured.
