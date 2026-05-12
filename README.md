# openclaw

## Project Title

A deterministic, local-first system engineered for precision, auditability, and controlled force.

## Overview

This repository provides a modular, persona-driven automation system designed for environments where clarity, reproducibility, and evidentiary integrity are non-negotiable. The architecture emphasizes deterministic execution, transparent state transitions, and strict separation between configuration, logic, and record.

## Features

- Local-first execution (no cloud dependency unless explicitly configured)
- Deterministic agent loops with reproducible outputs
- Persona-driven architecture (e.g., Shennell: Zero-Boundary)
- Modular skills, tools, and adapters
- Audit-ready logs and chronological traceability
- Optional Windows 11 `.exe` installer
- Evidence-indexed reasoning (if enabled)

## Installation (Windows 11)

A Windows-ready `.exe` installer is available for users who require a clean, offline-capable execution environment.

1. Go to the Releases page.
2. Download the latest `.exe` installer.
3. Run the installer and follow the prompts.
4. Launch the application from the Start Menu or desktop shortcut.
5. The system initializes with local configuration, persona files, and agent modules pre-loaded.

## Running the Application

After installation:

- Launch the application normally.
- The system loads its persona, skills, and configuration.
- Logs are written to the local `logs/` directory.
- All state transitions are deterministic and traceable.

## Configuration

Configuration files are stored in:

```text
config/
  agents/
  personas/
  skills/
  system.json
```

Modify these files to adjust behavior, enable or disable agents, or extend capabilities.

## Development

To run from source:

```bash
pip install -r requirements.txt
python your_entrypoint.py
```

## Building the Windows `.exe`

A GitHub Actions workflow automatically builds the `.exe` on tagged releases.

Manual build:

```bash
pyinstaller --onefile --noconsole your_entrypoint.py
```

Replace `your_entrypoint.py` with your actual entrypoint.

## Windows Installer UI Text Set

Installer dialog copy is maintained at:

- `installer/windows/INSTALLER_UI_TEXT.md`

## Shennell First-Run Message

First-run launch message content is stored at:

- `config/personas/shennell_first_run_message.txt`

## Architecture

Full system design, usage, operations reference, and architecture diagrams are in [ARCHITECTURE.md](ARCHITECTURE.md).

## License

MIT License.  
You may use, modify, and distribute this project with attribution.
