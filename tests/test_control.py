"""Tests for the control surface and safety gate."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import tempfile
import unittest
from openclaw.control.surface import ControlSurface
from openclaw.control.safety import SafetyGate, SafetyViolation


class TestControlSurface(unittest.TestCase):

    def test_default_construction(self):
        cs = ControlSurface()
        self.assertTrue(cs.persona.enforcement)
        self.assertTrue(cs.persona.speculation_block)
        self.assertTrue(cs.evidence.safe_mode)
        self.assertTrue(cs.evidence.chain_of_custody_enforcement)
        self.assertEqual(cs.determinism.mode, "strict")
        self.assertEqual(cs.logging.mode, "standard")

    def test_all_default_skills_enabled(self):
        cs = ControlSurface()
        for skill, enabled in cs.skills.enabled.items():
            self.assertTrue(enabled, f"Skill {skill!r} should be enabled by default")

    def test_all_default_agents_enabled(self):
        cs = ControlSurface()
        for agent, enabled in cs.agents.enabled.items():
            self.assertTrue(enabled, f"Agent {agent!r} should be enabled by default")

    def test_skill_allowed(self):
        cs = ControlSurface()
        cs.skills.enabled["calculator"] = False
        self.assertFalse(cs.skill_allowed("calculator"))
        self.assertTrue(cs.skill_allowed("get_datetime"))

    def test_agent_allowed(self):
        cs = ControlSurface()
        cs.agents.enabled["builder"] = False
        self.assertFalse(cs.agent_allowed("builder"))
        self.assertTrue(cs.agent_allowed("shennell"))

    def test_serialise_roundtrip(self):
        cs = ControlSurface()
        cs.skills.enabled["hash_file"] = False
        cs.logging.mode = "judicial"
        d = cs.to_dict()
        restored = ControlSurface.from_dict(d)
        self.assertFalse(restored.skills.enabled["hash_file"])
        self.assertEqual(restored.logging.mode, "judicial")

    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            cs = ControlSurface()
            cs.logging.mode = "judicial"
            cs.save(path)
            loaded = ControlSurface.load(path)
            self.assertEqual(loaded.logging.mode, "judicial")
        finally:
            os.unlink(path)

    def test_load_missing_file_returns_default(self):
        cs = ControlSurface.load("/nonexistent/path/surface.json")
        self.assertIsInstance(cs, ControlSurface)

    def test_active_tool_names_respects_disabling(self):
        cs = ControlSurface()
        cs.skills.enabled["calculator"] = False
        active = cs.active_tool_names()
        self.assertNotIn("calculator", active)
        self.assertIn("get_datetime", active)


class TestSafetyGate(unittest.TestCase):

    def test_known_forbidden_action(self):
        with self.assertRaises(SafetyViolation):
            SafetyGate.check_tool("overwrite_evidence", {})

    def test_system_path_blocked(self):
        with self.assertRaises(SafetyViolation):
            SafetyGate.check_tool("hash_file", {"path": "/etc/passwd"})

    def test_windows_system_path_blocked(self):
        with self.assertRaises(SafetyViolation):
            SafetyGate.check_tool("hash_file", {"path": "C:/Windows/system32/calc.exe"})

    def test_normal_path_allowed(self):
        # Should not raise
        SafetyGate.check_tool("hash_file", {"path": "/home/user/document.txt"})

    def test_calculator_allowed(self):
        SafetyGate.check_tool("calculator", {"expression": "2 + 2"})

    def test_hard_rules_present(self):
        rules = SafetyGate.hard_rules()
        self.assertGreater(len(rules), 0)
        for rule_id, desc in rules:
            self.assertIsInstance(rule_id, str)
            self.assertIsInstance(desc, str)

    def test_assert_evidence_safe_raises_on_modified(self):
        with self.assertRaises(SafetyViolation):
            SafetyGate.assert_evidence_safe("/some/file.txt", modified=True)

    def test_assert_evidence_safe_passes_on_unmodified(self):
        # Should not raise
        SafetyGate.assert_evidence_safe("/some/file.txt", modified=False)


if __name__ == "__main__":
    unittest.main()
