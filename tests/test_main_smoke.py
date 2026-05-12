import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class MainSmokeTest(unittest.TestCase):
    def test_main_starts_successfully(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "main.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("openclaw started", result.stdout)


if __name__ == "__main__":
    unittest.main()
