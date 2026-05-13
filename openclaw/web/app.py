"""Flask-based local web interface for OpenClaw.

Serves on 127.0.0.1 only. Never exposed to external networks.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import threading
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, render_template, request

from ..ai.agent import Agent
from ..ai.orchestrator import Orchestrator
from ..control import ControlSurface, SafetyGate, SafetyViolation, get_surface, save_surface
from ..personas import list_personas

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.urandom(24)

# In-memory log buffer for the log viewer
_log_buffer: List[Dict[str, Any]] = []
_log_lock = threading.Lock()

_orchestrator = Orchestrator()
_current_persona = "shennell"


class BufferingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        with _log_lock:
            _log_buffer.append(
                {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "level": record.levelname,
                    "component": record.name,
                    "message": self.format(record),
                }
            )
            if len(_log_buffer) > 500:
                _log_buffer.pop(0)


logging.getLogger("openclaw").addHandler(BufferingHandler())
logging.getLogger("openclaw").setLevel(logging.DEBUG)


# ── routes ─────────────────────────────────────────────────────────────


@app.route("/")
def index() -> str:
    return render_template("index.html")


# ── chat API ───────────────────────────────────────────────────────────


@app.route("/api/chat", methods=["POST"])
def api_chat() -> Response:
    data = request.get_json(force=True, silent=True) or {}
    user_input: str = str(data.get("message", "")).strip()
    persona_name: str = str(data.get("persona", _current_persona)).strip()

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    surface = get_surface()
    if not surface.agent_allowed(persona_name):
        return jsonify(
            {
                "error": f"Agent '{persona_name}' is currently disabled on the control surface.",
                "persona": persona_name,
            }
        ), 403

    try:
        agent = _orchestrator.agent(persona_name)
        response = agent.chat(user_input)
        return jsonify(
            {
                "response": response,
                "persona": agent.persona.name,
                "backend": agent.backend_name,
            }
        )
    except Exception:
        logger.exception("Chat endpoint error (persona=%s)", persona_name)
        return jsonify({"error": "An internal error occurred. Check server logs."}), 500


@app.route("/api/chat/reset", methods=["POST"])
def api_chat_reset() -> Response:
    data = request.get_json(force=True, silent=True) or {}
    persona_name = str(data.get("persona", _current_persona))
    _orchestrator.agent(persona_name).reset()
    return jsonify({"ok": True})


# ── control surface API ────────────────────────────────────────────────


@app.route("/api/control", methods=["GET"])
def api_control_get() -> Response:
    return jsonify(get_surface().to_dict())


@app.route("/api/control", methods=["POST"])
def api_control_set() -> Response:
    """
    Update control surface settings.

    Accepts a partial JSON object; only provided keys are updated.
    Hard safety rules are always enforced — attempts to override them are rejected.
    """
    data = request.get_json(force=True, silent=True) or {}
    surface = get_surface()
    current = surface.to_dict()

    # Deep-merge incoming data
    def deep_merge(base: dict, override: dict) -> dict:
        result = dict(base)
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(result.get(k), dict):
                result[k] = deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    merged = deep_merge(current, data)

    try:
        updated = ControlSurface.from_dict(merged)
    except Exception:
        logger.exception("Control surface update rejected")
        return jsonify({"error": "Invalid settings. Check server logs for details."}), 400

    # Replace singleton
    import openclaw.control.surface as _cs_mod
    _cs_mod._surface = updated
    save_surface()
    return jsonify(updated.to_dict())


# ── personas API ───────────────────────────────────────────────────────


@app.route("/api/personas", methods=["GET"])
def api_personas() -> Response:
    return jsonify(
        {
            name: {
                "name": p.name,
                "role": p.role,
                "voice": p.voice,
                "hard_boundaries": p.hard_boundaries,
                "forbidden_actions": p.forbidden_actions,
            }
            for name, p in list_personas().items()
        }
    )


# ── skills / tools API ─────────────────────────────────────────────────


@app.route("/api/skills", methods=["GET"])
def api_skills() -> Response:
    from ..ai.tools import TOOL_SCHEMAS

    surface = get_surface()
    skills = [
        {
            "name": s["function"]["name"],
            "description": s["function"]["description"],
            "enabled": surface.skill_allowed(s["function"]["name"]),
        }
        for s in TOOL_SCHEMAS
    ]
    return jsonify(skills)


# ── safety API ─────────────────────────────────────────────────────────


@app.route("/api/safety/rules", methods=["GET"])
def api_safety_rules() -> Response:
    return jsonify(
        [{"id": rid, "description": desc} for rid, desc in SafetyGate.hard_rules()]
    )


# ── logs API ───────────────────────────────────────────────────────────


@app.route("/api/logs", methods=["GET"])
def api_logs() -> Response:
    with _log_lock:
        logs = list(_log_buffer)
    level = request.args.get("level", "").upper()
    if level:
        logs = [l for l in logs if l["level"] == level]
    return jsonify(logs[-200:])


@app.route("/api/logs/clear", methods=["POST"])
def api_logs_clear() -> Response:
    with _log_lock:
        _log_buffer.clear()
    return jsonify({"ok": True})


# ── evidence / chronology passthrough ─────────────────────────────────


@app.route("/api/evidence", methods=["GET"])
def api_evidence() -> Response:
    from ..ai.tools import list_evidence

    try:
        return jsonify({"result": list_evidence()})
    except Exception:
        logger.exception("Evidence list error")
        return jsonify({"error": "Failed to load evidence index."}), 500


@app.route("/api/chronology", methods=["GET"])
def api_chronology() -> Response:
    from ..ai.tools import list_chronology

    try:
        return jsonify({"result": list_chronology()})
    except Exception:
        logger.exception("Chronology list error")
        return jsonify({"error": "Failed to load chronology."}), 500


# ── runner ─────────────────────────────────────────────────────────────


def run(host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> None:
    """Start the Flask web server."""
    print(f"\n  OpenClaw Web UI  →  http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
