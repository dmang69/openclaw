"""Tests for the persona system."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from openclaw.personas import get_persona, list_personas, SHENNELL, ANALYST, BUILDER
from openclaw.personas.base import Persona


class TestPersonaRegistry(unittest.TestCase):

    def test_list_personas_returns_all(self):
        personas = list_personas()
        self.assertIn("shennell", personas)
        self.assertIn("analyst", personas)
        self.assertIn("builder", personas)

    def test_get_persona_case_insensitive(self):
        self.assertIs(get_persona("Shennell"), SHENNELL)
        self.assertIs(get_persona("ANALYST"), ANALYST)

    def test_get_persona_unknown_falls_back_to_shennell(self):
        p = get_persona("nonexistent_persona")
        self.assertIs(p, SHENNELL)

    def test_personas_have_required_fields(self):
        for name, p in list_personas().items():
            self.assertIsInstance(p.name, str)
            self.assertIsInstance(p.role, str)
            self.assertIsInstance(p.voice, str)
            self.assertIsInstance(p.system_prompt_addition, str)
            self.assertIsInstance(p.hard_boundaries, list)
            self.assertIsInstance(p.forbidden_actions, list)


class TestShennell(unittest.TestCase):

    def test_forbids_fabrication(self):
        self.assertFalse(SHENNELL.allows_action("fabrication"))

    def test_forbids_speculation(self):
        self.assertFalse(SHENNELL.allows_action("speculation"))

    def test_allows_unknown_action(self):
        self.assertTrue(SHENNELL.allows_action("calculate"))

    def test_has_hard_boundaries(self):
        self.assertGreater(len(SHENNELL.hard_boundaries), 0)

    def test_get_system_prompt_contains_addition(self):
        prompt = SHENNELL.get_system_prompt()
        self.assertIn("Shennell", prompt)

    def test_boundary_message_on_ambiguity(self):
        msg = SHENNELL.boundary_message("ambiguity")
        self.assertIsInstance(msg, str)
        self.assertGreater(len(msg), 5)

    def test_boundary_message_default(self):
        msg = SHENNELL.boundary_message("undefined_situation")
        self.assertIsInstance(msg, str)
        self.assertGreater(len(msg), 5)


class TestAnalyst(unittest.TestCase):

    def test_name(self):
        self.assertEqual(ANALYST.name, "Analyst")

    def test_forbids_fabrication(self):
        self.assertFalse(ANALYST.allows_action("fabrication"))


class TestBuilder(unittest.TestCase):

    def test_name(self):
        self.assertEqual(BUILDER.name, "Builder")

    def test_forbids_insecure_code(self):
        self.assertFalse(BUILDER.allows_action("insecure_code"))


if __name__ == "__main__":
    unittest.main()
