#!/usr/bin/env python3
"""OpenClaw — entry point.

Usage:
  python main.py              # launch CLI (default)
  python main.py --web        # launch web UI on http://127.0.0.1:5000
  python main.py --web --port 8080
  python main.py --cli        # explicit CLI mode
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OpenClaw — open-source AI assistant with persona control surface"
    )
    parser.add_argument("--web", action="store_true", help="Launch web UI")
    parser.add_argument("--cli", action="store_true", help="Launch CLI (default)")
    parser.add_argument("--host", default="127.0.0.1", help="Web host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Web port (default: 5000)")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()

    if args.web:
        # Try to open browser automatically
        import threading
        import webbrowser

        url = f"http://{args.host}:{args.port}"
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

        from openclaw.web import run
        run(host=args.host, port=args.port, debug=args.debug)
    else:
        from openclaw.cli import run_cli
        run_cli()


if __name__ == "__main__":
    main()
