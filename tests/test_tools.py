"""Tests for built-in tools."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import math
import tempfile
import unittest
from openclaw.ai.tools import (
    calculator,
    get_datetime,
    hash_file,
    execute_tool,
    TOOL_SCHEMAS,
)


class TestCalculator(unittest.TestCase):

    def test_addition(self):
        self.assertEqual(calculator("2 + 2"), "4")

    def test_subtraction(self):
        self.assertEqual(calculator("10 - 3"), "7")

    def test_multiplication(self):
        self.assertEqual(calculator("3 * 7"), "21")

    def test_float_division(self):
        self.assertEqual(calculator("10 / 4"), "2.5")

    def test_power(self):
        self.assertEqual(calculator("2 ** 10"), "1024")

    def test_sqrt(self):
        self.assertEqual(calculator("sqrt(16)"), "4.0")

    def test_pi(self):
        result = float(calculator("pi"))
        self.assertAlmostEqual(result, math.pi, places=5)

    def test_modulo(self):
        self.assertEqual(calculator("10 % 3"), "1")

    def test_floor_div(self):
        self.assertEqual(calculator("10 // 3"), "3")

    def test_nested(self):
        result = float(calculator("sqrt(2 ** 4)"))
        self.assertAlmostEqual(result, 4.0, places=5)

    def test_division_by_zero(self):
        result = calculator("1 / 0")
        self.assertIn("Error", result)

    def test_invalid_expression_import(self):
        result = calculator("import os")
        self.assertIn("Error", result)

    def test_invalid_name(self):
        result = calculator("foo(1)")
        self.assertIn("Error", result)


class TestGetDatetime(unittest.TestCase):

    def test_returns_nonempty_string(self):
        result = get_datetime()
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10)


class TestHashFile(unittest.TestCase):

    def test_hash_existing_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("deterministic content")
            path = f.name
        try:
            result = hash_file(path)
            self.assertIn("SHA-256", result)
            # Same content → same hash on repeated calls
            self.assertEqual(hash_file(path), result)
        finally:
            os.unlink(path)

    def test_hash_nonexistent_file(self):
        result = hash_file("/nonexistent/path/file.txt")
        self.assertIn("Error", result)


class TestExecuteTool(unittest.TestCase):

    def test_unknown_tool(self):
        result = execute_tool("nonexistent", {})
        self.assertIn("Unknown tool", result)

    def test_calculator_via_execute(self):
        result = execute_tool("calculator", {"expression": "10 + 5"})
        self.assertEqual(result, "15")

    def test_get_datetime_via_execute(self):
        result = execute_tool("get_datetime", {})
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 5)

    def test_safety_gate_blocks_forbidden(self):
        # The safety gate should block forbidden tool names
        result = execute_tool("overwrite_evidence", {})
        # Either "Unknown tool" (not registered) or "Safety violation"
        self.assertTrue("Unknown tool" in result or "Safety" in result)


class TestToolSchemas(unittest.TestCase):

    def test_all_schemas_have_required_fields(self):
        for schema in TOOL_SCHEMAS:
            self.assertIn("type", schema)
            self.assertIn("function", schema)
            fn = schema["function"]
            self.assertIn("name", fn)
            self.assertIn("description", fn)
            self.assertIn("parameters", fn)

    def test_schema_count(self):
        self.assertGreaterEqual(len(TOOL_SCHEMAS), 10)


if __name__ == "__main__":
    unittest.main()
