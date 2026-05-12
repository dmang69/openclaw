# openclaw

## Project Description

A modular, audit-friendly system designed for reliability, transparency, and maintainability. Built with a focus on clean architecture, reproducible workflows, and clear separation of concerns, this repository provides a structured foundation for iterative development, testing, and deployment across multiple environments.

## Installation on Windows 11 (.exe)

This project provides a Windows-ready `.exe` build for users who require a clean, deterministic, local-first execution environment. The installer bundles required components so the system can run without external dependencies.

### Steps

1. Navigate to the **Releases** section of this repository.
2. Download the latest Windows `.exe` installer.
3. Run the installer and follow the on-screen instructions.
4. Launch the application from the Start Menu or desktop shortcut.
5. On first run, the system initializes local configuration, persona files, and agent modules.

### Execution Model

- Fully offline-capable
- Deterministic agent loops
- Transparent logs and reproducible state transitions
- No hidden processes or network calls unless explicitly configured

This installation path is designed for environments where auditability, predictability, and local control are non-negotiable.

## Releases

Each release includes a Windows 11 `.exe` installer and supporting artifacts. Builds are versioned and packaged for deterministic local execution.

### Included in Each Release

- Windows Installer (`.exe`) — full local-first runtime
- Changelog — structured summary of changes
- Hash File (SHA-256) — for integrity verification
- Portable Build (optional) — standalone binary without installer
- Spec File / Build Metadata — for reproducibility

### Release Channels

- **Stable** — production-ready, fully validated
- **Preview** — new features under evaluation
- **Nightly** — experimental builds for testing

Users who require reliability should remain on the **Stable** channel.

## Installer Welcome Message (Shennell Voice)

Shennell is the default installer persona voice used by this project.

Welcome. I am Shennell.  
You are installing a system built on constraint, clarity, and accountability.  
I do not rely on external services. I do not guess. I do not wander.  
Every action I take is traceable. Every inference is anchored to disclosed evidence.  
Once installed, I operate locally, with deterministic loops and transparent state transitions.  
If you proceed, expect precision. Expect discipline. Expect form that does not break.
