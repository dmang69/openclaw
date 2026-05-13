#!/usr/bin/env python3
"""OpenClaw — entry point."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openclaw.cli import run_cli

if __name__ == "__main__":
    run_cli()
