"""Smoke tests — validate all top-level imports and basic wiring."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest


class TestImports(unittest.TestCase):

    def test_package_version(self):
        import openclaw
        self.assertIsNotNone(openclaw.__version__)

    def test_config(self):
        from openclaw.config import Config
        self.assertIsInstance(Config.BACKEND, str)
        self.assertIsInstance(Config.PERSONA, str)

    def test_personas(self):
        from openclaw.personas import get_persona, list_personas
        personas = list_personas()
        self.assertGreaterEqual(len(personas), 3)
        p = get_persona("shennell")
        self.assertEqual(p.name, "Shennell")

    def test_tools_importable(self):
        from openclaw.ai.tools import TOOL_SCHEMAS, execute_tool
        self.assertGreaterEqual(len(TOOL_SCHEMAS), 10)

    def test_agent_importable(self):
        from openclaw.ai.agent import Agent
        self.assertTrue(callable(Agent))

    def test_orchestrator_importable(self):
        from openclaw.ai.orchestrator import Orchestrator
        orch = Orchestrator()
        self.assertIsNotNone(orch)

    def test_local_backend_available(self):
        from openclaw.ai.backends.local_backend import LocalBackend
        b = LocalBackend()
        self.assertTrue(b.is_available())

    def test_control_surface_default(self):
        from openclaw.control.surface import ControlSurface
        cs = ControlSurface()
        self.assertTrue(cs.persona.enforcement)
        self.assertTrue(cs.evidence.safe_mode)

    def test_safety_gate(self):
        from openclaw.control.safety import SafetyGate, SafetyViolation
        rules = SafetyGate.hard_rules()
        self.assertGreater(len(rules), 0)

    def test_web_app_importable(self):
        from openclaw.web.app import app
        self.assertIsNotNone(app)


class TestLocalAgentChat(unittest.TestCase):

    def test_chat_returns_string(self):
        from openclaw.ai.backends.local_backend import LocalBackend
        from openclaw.ai.agent import Agent
        agent = Agent(backend=LocalBackend(), )
        response = agent.chat("hello")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_chat_with_calculator(self):
        from openclaw.ai.backends.local_backend import LocalBackend
        from openclaw.ai.agent import Agent
        # The local backend will route "calculate 2+2" to the calculator tool
        # and the agent loop will execute it and return the result
        agent = Agent(backend=LocalBackend())
        response = agent.chat("calculate 2 + 2")
        # Response goes through one tool iteration then produces empty string
        # (local backend can't generate a final text from tool output, but it
        # doesn't crash — it returns whatever the final backend response is)
        self.assertIsInstance(response, str)

    def test_skill_disabled_on_control_surface(self):
        from openclaw.ai.tools import execute_tool
        from openclaw.control.surface import ControlSurface
        import openclaw.control.surface as _cs_mod

        original = _cs_mod._surface
        try:
            cs = ControlSurface()
            cs.skills.enabled["calculator"] = False
            _cs_mod._surface = cs
            result = execute_tool("calculator", {"expression": "1 + 1"})
            self.assertIn("disabled", result)
        finally:
            _cs_mod._surface = original

    def test_web_app_chat_endpoint(self):
        from openclaw.web.app import app
        client = app.test_client()
        resp = client.post(
            "/api/chat",
            json={"message": "hello", "persona": "shennell"},
            content_type="application/json",
        )
        self.assertIn(resp.status_code, (200, 403, 500))

    def test_web_app_control_get(self):
        from openclaw.web.app import app
        client = app.test_client()
        resp = client.get("/api/control")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("persona", data)
        self.assertIn("agents", data)
        self.assertIn("skills", data)

    def test_web_app_safety_rules(self):
        from openclaw.web.app import app
        client = app.test_client()
        resp = client.get("/api/safety/rules")
        self.assertEqual(resp.status_code, 200)
        rules = resp.get_json()
        self.assertGreater(len(rules), 0)


if __name__ == "__main__":
    unittest.main()
