# Contributing to OpenClaw

## Philosophy

OpenClaw is built on determinism, auditability, and controlled force. Every contribution must preserve these principles.

## Standards

- **Deterministic functions only** — same inputs must produce same outputs
- **No silent failures** — all errors must be surfaced and logged
- **No fabrication** — never generate output that misrepresents facts
- **Persona-safe code** — skills must respect persona constraints before executing
- **Evidence integrity** — never modify original files; always hash before parsing

## Setup

```bash
git clone https://github.com/dmang69/openclaw
cd openclaw
python -m venv venv
# Windows: venv\Scripts\activate   Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Pull Request Requirements

1. All tests must pass
2. New features require tests
3. Persona constraint logic changes require persona tests
4. Evidence-handling changes require evidence integrity review
5. Safety gate changes require explicit security justification

## Commit Messages

```
[component] Short description

Examples:
  [persona] Add creativity-block to Analyst persona
  [tools] Add PDF evidence parser with hash logging
  [web] Add skill-level debugging inspector
  [safety] Strengthen path validation in SafetyGate
```

## Adding a Persona

1. Create `openclaw/personas/yourpersona.py` using the `Persona` dataclass
2. Register it in `openclaw/personas/__init__.py`
3. Add tests in `tests/test_personas.py`

## Adding a Skill (Tool)

1. Implement the function in `openclaw/ai/tools.py`
2. Add a JSON schema to `TOOL_SCHEMAS`
3. Register the function in `_TOOL_FUNCTIONS`
4. Add tests in `tests/test_tools.py`

## Shennell's Developer Oath

> I will not introduce drift.  
> I will not hide state.  
> I will not fabricate outputs or infer beyond evidence.  
> I will write code that can be traced, defended, and audited.  
> I will respect persona boundaries and system constraints.
