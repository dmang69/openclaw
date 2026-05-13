"""Tests for ConversationMemory."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from openclaw.ai.memory import ConversationMemory


class TestConversationMemory(unittest.TestCase):

    def test_add_user(self):
        mem = ConversationMemory()
        mem.add_user("hello")
        self.assertEqual(len(mem), 1)
        self.assertEqual(mem.get_messages()[0]["role"], "user")

    def test_add_assistant(self):
        mem = ConversationMemory()
        mem.add_assistant("hi there")
        msgs = mem.get_messages()
        self.assertEqual(msgs[0]["role"], "assistant")
        self.assertEqual(msgs[0]["content"], "hi there")

    def test_add_tool_result(self):
        mem = ConversationMemory()
        mem.add_tool_result("tc-1", "calculator", "42")
        msgs = mem.get_messages()
        self.assertEqual(msgs[0]["role"], "tool")
        self.assertEqual(msgs[0]["content"], "42")

    def test_clear(self):
        mem = ConversationMemory()
        mem.add_user("hello")
        mem.clear()
        self.assertEqual(len(mem), 0)

    def test_trim(self):
        mem = ConversationMemory(max_messages=3)
        for i in range(5):
            mem.add_user(f"msg {i}")
        self.assertEqual(len(mem), 3)
        # Should keep the most recent messages
        self.assertEqual(mem.get_messages()[-1]["content"], "msg 4")

    def test_get_messages_returns_copy(self):
        mem = ConversationMemory()
        mem.add_user("hello")
        msgs = mem.get_messages()
        msgs.clear()
        self.assertEqual(len(mem), 1)


if __name__ == "__main__":
    unittest.main()
