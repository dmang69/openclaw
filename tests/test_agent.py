"""Tests for the AI agent (using mock backends)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from openclaw.ai.agent import Agent
from openclaw.ai.backends.base import Backend, BackendResponse
from openclaw.ai.backends.local_backend import LocalBackend
from openclaw.ai.tools import TOOL_SCHEMAS
from openclaw.personas import SHENNELL, ANALYST


class MockBackend(Backend):
    """Backend that returns preset responses in order."""

    def __init__(self, responses):
        self._responses = iter(responses)

    @property
    def name(self):
        return "Mock"

    def is_available(self):
        return True

    def complete(self, messages, tools=None):
        try:
            return next(self._responses)
        except StopIteration:
            return BackendResponse(content="(mock exhausted)", tool_calls=[])


class TestAgent(unittest.TestCase):

    def test_simple_chat(self):
        backend = MockBackend([BackendResponse(content="Hello!", tool_calls=[])])
        agent = Agent(backend=backend, persona=SHENNELL)
        response = agent.chat("hi")
        self.assertEqual(response, "Hello!")

    def test_chat_with_tool_call(self):
        backend = MockBackend([
            BackendResponse(
                content=None,
                tool_calls=[{"id": "t1", "name": "calculator", "arguments": {"expression": "2 + 2"}}],
            ),
            BackendResponse(content="The answer is 4.", tool_calls=[]),
        ])
        agent = Agent(backend=backend, persona=SHENNELL)
        response = agent.chat("what is 2+2?")
        self.assertEqual(response, "The answer is 4.")

    def test_reset_clears_history(self):
        backend = MockBackend([
            BackendResponse(content="resp1", tool_calls=[]),
        ])
        agent = Agent(backend=backend, persona=SHENNELL)
        agent.chat("hello")
        agent.reset()
        self.assertEqual(len(agent.history()), 0)

    def test_history_grows(self):
        backend = MockBackend([
            BackendResponse(content="resp1", tool_calls=[]),
            BackendResponse(content="resp2", tool_calls=[]),
        ])
        agent = Agent(backend=backend, persona=SHENNELL)
        agent.chat("msg1")
        agent.chat("msg2")
        # Each chat adds user + assistant = 2 messages each → 4 total
        self.assertEqual(len(agent.history()), 4)

    def test_set_persona(self):
        backend = MockBackend([BackendResponse(content="ok", tool_calls=[])])
        agent = Agent(backend=backend, persona=SHENNELL)
        agent.set_persona("analyst")
        self.assertEqual(agent.persona.name, "Analyst")
        # History cleared on persona switch
        self.assertEqual(len(agent.history()), 0)

    def test_backend_name(self):
        backend = MockBackend([])
        agent = Agent(backend=backend)
        self.assertEqual(agent.backend_name, "Mock")


class TestLocalBackend(unittest.TestCase):

    def setUp(self):
        self.backend = LocalBackend(persona_name="shennell")

    def test_greeting(self):
        resp = self.backend.complete(
            [{"role": "user", "content": "hello"}], tools=TOOL_SCHEMAS
        )
        self.assertIsNotNone(resp.content)
        self.assertIn("Hello", resp.content)

    def test_math_routes_to_calculator(self):
        resp = self.backend.complete(
            [{"role": "user", "content": "calculate 5 + 3"}], tools=TOOL_SCHEMAS
        )
        self.assertTrue(resp.has_tool_calls)
        self.assertEqual(resp.tool_calls[0]["name"], "calculator")
        self.assertEqual(resp.tool_calls[0]["arguments"]["expression"], "5 + 3")

    def test_time_routes_to_get_datetime(self):
        resp = self.backend.complete(
            [{"role": "user", "content": "what time is it?"}], tools=TOOL_SCHEMAS
        )
        self.assertTrue(resp.has_tool_calls)
        self.assertEqual(resp.tool_calls[0]["name"], "get_datetime")

    def test_list_notes_routes_correctly(self):
        resp = self.backend.complete(
            [{"role": "user", "content": "list my notes"}], tools=TOOL_SCHEMAS
        )
        self.assertTrue(resp.has_tool_calls)
        self.assertEqual(resp.tool_calls[0]["name"], "list_notes")

    def test_list_evidence_routes_correctly(self):
        resp = self.backend.complete(
            [{"role": "user", "content": "show my evidence"}], tools=TOOL_SCHEMAS
        )
        self.assertTrue(resp.has_tool_calls)
        self.assertEqual(resp.tool_calls[0]["name"], "list_evidence")

    def test_help_response(self):
        resp = self.backend.complete(
            [{"role": "user", "content": "help"}], tools=TOOL_SCHEMAS
        )
        self.assertIsNotNone(resp.content)
        self.assertFalse(resp.has_tool_calls)


if __name__ == "__main__":
    unittest.main()
