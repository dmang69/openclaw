"""Built-in tools for the OpenClaw agent.

Includes:
  - calculator        safe math expression evaluator
  - get_datetime      current date/time
  - save_note         persist a note to disk
  - list_notes        list saved notes
  - read_note         read a saved note
  - hash_file         SHA-256 hash of a local file
  - index_evidence    ingest a file into the evidence index with hash + metadata
  - list_evidence     list all indexed evidence
  - add_chronology_event  record a timestamped event in the timeline
  - list_chronology   show the chronological timeline
"""

from __future__ import annotations

import ast
import datetime
import hashlib
import json
import math
import operator
import os
import re
from typing import Any, Callable, Dict, List

from ..config import Config


# ─────────────────────────── safe evaluator ───────────────────────────

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SAFE_FUNCTIONS: Dict[str, Any] = {
    "abs": abs,
    "round": round,
    "sqrt": math.sqrt,
    "ceil": math.ceil,
    "floor": math.floor,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "exp": math.exp,
    "pi": math.pi,
    "e": math.e,
    "pow": pow,
    "min": min,
    "max": max,
}


def _safe_eval(node: ast.expr) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in _SAFE_FUNCTIONS:
            return _SAFE_FUNCTIONS[node.id]
        raise ValueError(f"Unknown name: {node.id!r}")
    if isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op}")
        return _SAFE_OPERATORS[op](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op}")
        return _SAFE_OPERATORS[op](_safe_eval(node.operand))
    if isinstance(node, ast.Call):
        func = _safe_eval(node.func)
        args = [_safe_eval(a) for a in node.args]
        return func(*args)
    raise ValueError(f"Unsupported expression type: {type(node).__name__}")


# ─────────────────────────── tool functions ───────────────────────────


def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as exc:
        return f"Error: {exc}"


def get_datetime() -> str:
    """Return the current date and time."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")


def save_note(title: str, content: str) -> str:
    """Save a note to the notes directory."""
    try:
        os.makedirs(Config.NOTES_DIR, exist_ok=True)
        safe = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
        path = os.path.join(Config.NOTES_DIR, f"{safe}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"Created: {datetime.datetime.now().isoformat()}\n\n")
            f.write(content)
        return f"Note saved: {path}"
    except Exception as exc:
        return f"Error saving note: {exc}"


def list_notes() -> str:
    """List all saved notes."""
    try:
        if not os.path.isdir(Config.NOTES_DIR):
            return "No notes found."
        files = sorted(f for f in os.listdir(Config.NOTES_DIR) if f.endswith(".txt"))
        if not files:
            return "No notes found."
        return "Saved notes:\n" + "\n".join(f"  - {f[:-4].replace('_', ' ')}" for f in files)
    except Exception as exc:
        return f"Error listing notes: {exc}"


def read_note(title: str) -> str:
    """Read a saved note by title."""
    try:
        safe = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
        path = os.path.join(Config.NOTES_DIR, f"{safe}.txt")
        if not os.path.isfile(path):
            return f"Note not found: {title!r}"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        return f"Error reading note: {exc}"


def hash_file(path: str) -> str:
    """Compute the SHA-256 hash of a file."""
    try:
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            return f"Error: file not found: {path!r}"
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return f"SHA-256: {h.hexdigest()}  ({path})"
    except Exception as exc:
        return f"Error hashing file: {exc}"


def _evidence_index_path() -> str:
    return os.path.join(Config.EVIDENCE_DIR, "index.json")


def _load_evidence_index() -> List[Dict[str, Any]]:
    p = _evidence_index_path()
    if not os.path.isfile(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_evidence_index(index: List[Dict[str, Any]]) -> None:
    os.makedirs(Config.EVIDENCE_DIR, exist_ok=True)
    with open(_evidence_index_path(), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


def index_evidence(path: str, notes: str = "") -> str:
    """
    Ingest a file into the evidence index.

    Computes the SHA-256 hash, records metadata (size, timestamps), and
    stores an immutable chain-of-custody entry. The original file is never
    modified.
    """
    try:
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            return f"Error: file not found: {path!r}"
        h = hashlib.sha256()
        with open(path, "rb") as f:
            raw = f.read()
            h.update(raw)
        digest = h.hexdigest()
        stat = os.stat(path)
        entry: Dict[str, Any] = {
            "id": f"ev-{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "path": os.path.abspath(path),
            "filename": os.path.basename(path),
            "sha256": digest,
            "size_bytes": stat.st_size,
            "indexed_at": datetime.datetime.now().isoformat(),
            "notes": notes,
            "chain_of_custody": [
                {
                    "action": "ingest",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "actor": "system",
                }
            ],
        }
        index = _load_evidence_index()
        # Avoid duplicate ingestion of the same file+hash
        for existing in index:
            if existing.get("sha256") == digest and existing.get("path") == entry["path"]:
                return f"Evidence already indexed (id={existing['id']}, sha256={digest[:16]}…)"
        index.append(entry)
        _save_evidence_index(index)
        return (
            f"Evidence indexed:\n"
            f"  ID:      {entry['id']}\n"
            f"  File:    {entry['filename']}\n"
            f"  SHA-256: {digest[:32]}…\n"
            f"  Size:    {stat.st_size} bytes\n"
            f"  Stored:  {_evidence_index_path()}"
        )
    except Exception as exc:
        return f"Error indexing evidence: {exc}"


def list_evidence() -> str:
    """List all indexed evidence items."""
    try:
        index = _load_evidence_index()
        if not index:
            return "No evidence indexed yet."
        lines = [f"Indexed evidence ({len(index)} item(s)):"]
        for e in index:
            lines.append(
                f"  [{e['id']}] {e['filename']}  sha256={e['sha256'][:16]}…  "
                f"({e['indexed_at'][:10]})"
            )
        return "\n".join(lines)
    except Exception as exc:
        return f"Error listing evidence: {exc}"


def _chronology_path() -> str:
    return os.path.join(Config.CHRONOLOGY_DIR, "timeline.json")


def _load_timeline() -> List[Dict[str, Any]]:
    p = _chronology_path()
    if not os.path.isfile(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_timeline(timeline: List[Dict[str, Any]]) -> None:
    os.makedirs(Config.CHRONOLOGY_DIR, exist_ok=True)
    with open(_chronology_path(), "w", encoding="utf-8") as f:
        json.dump(sorted(timeline, key=lambda x: x.get("event_timestamp", "")), f, indent=2)


def add_chronology_event(event_timestamp: str, description: str, evidence_id: str = "") -> str:
    """
    Add a timestamped event to the chronological timeline.

    event_timestamp should be ISO-8601 (e.g. '2025-03-14T09:30:00').
    """
    try:
        # Validate timestamp
        datetime.datetime.fromisoformat(event_timestamp)
        event: Dict[str, Any] = {
            "id": f"evt-{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "event_timestamp": event_timestamp,
            "description": description,
            "evidence_id": evidence_id,
            "recorded_at": datetime.datetime.now().isoformat(),
        }
        timeline = _load_timeline()
        timeline.append(event)
        _save_timeline(timeline)
        return f"Event recorded:\n  ID: {event['id']}\n  When: {event_timestamp}\n  Description: {description}"
    except ValueError as exc:
        return f"Error: invalid timestamp — {exc}. Use ISO-8601 format, e.g. '2025-03-14T09:30:00'."
    except Exception as exc:
        return f"Error recording event: {exc}"


def list_chronology() -> str:
    """Display the chronological timeline of events."""
    try:
        timeline = _load_timeline()
        if not timeline:
            return "No chronology events recorded yet."
        lines = [f"Chronology ({len(timeline)} event(s)):"]
        for ev in timeline:
            ref = f"  [ev_id={ev['evidence_id']}]" if ev.get("evidence_id") else ""
            lines.append(f"  {ev['event_timestamp'][:19]}  {ev['description']}{ref}")
        return "\n".join(lines)
    except Exception as exc:
        return f"Error reading chronology: {exc}"


# ─────────────────────────── registry ─────────────────────────────────

_TOOL_FUNCTIONS: Dict[str, Callable] = {
    "calculator": calculator,
    "get_datetime": get_datetime,
    "save_note": save_note,
    "list_notes": list_notes,
    "read_note": read_note,
    "hash_file": hash_file,
    "index_evidence": index_evidence,
    "list_evidence": list_evidence,
    "add_chronology_event": add_chronology_event,
    "list_chronology": list_chronology,
}

TOOL_SCHEMAS: List[Dict] = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression. Supports +, -, *, /, **, %, sqrt, sin, cos, log, exp, pi, e, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate, e.g. 'sqrt(16)' or '2 ** 10'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get the current date and time.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Save a note with a title and content to persistent storage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Note content"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "List all saved notes.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_note",
            "description": "Read a saved note by its title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the note to read"}
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hash_file",
            "description": "Compute the SHA-256 hash of a local file for integrity verification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or ~ path to the file"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "index_evidence",
            "description": (
                "Ingest a file into the evidence index. Computes SHA-256 hash, records file "
                "metadata, and stores an immutable chain-of-custody entry. The original file "
                "is never modified."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the evidence file"},
                    "notes": {
                        "type": "string",
                        "description": "Optional provenance notes",
                        "default": "",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_evidence",
            "description": "List all indexed evidence items with their IDs and hashes.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_chronology_event",
            "description": "Record a timestamped event in the chronological timeline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_timestamp": {
                        "type": "string",
                        "description": "ISO-8601 timestamp of the event, e.g. '2025-03-14T09:30:00'",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the event",
                    },
                    "evidence_id": {
                        "type": "string",
                        "description": "Optional evidence ID to link to this event",
                        "default": "",
                    },
                },
                "required": ["event_timestamp", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_chronology",
            "description": "Display the chronological timeline of all recorded events.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a registered tool by name with the given arguments."""
    func = _TOOL_FUNCTIONS.get(name)
    if func is None:
        return f"Unknown tool: {name!r}"
    try:
        return str(func(**arguments))
    except Exception as exc:
        return f"Tool execution error: {exc}"
