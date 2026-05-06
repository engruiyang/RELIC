# AGENTS.md

## Project

This repository is for RELIC, a Python-based attention training system using a single-channel BCI headset and the HNNK platform IPC interface.

## Language and style

- Use Python 3.10+.
- Keep modules small and readable.
- Prefer standard library first.
- Avoid unnecessary dependencies.
- Keep UI, protocol parsing, state estimation, game logic, and data recording separated.

## Architecture

Recommended modules:

- relic_core/ipc_client.py
- relic_core/focus_model.py
- relic_core/state_machine.py
- relic_core/difficulty.py
- relic_core/session_recorder.py
- relic_core/mock_data_source.py
- app/main_window.py
- app/game_fragment_lock.py

## Development priority

Build the project in this order:

1. IPC connection and raw message logging.
2. Attention value parsing.
3. Mock data source.
4. Focus Index calculation.
5. Fragment Lock MVP.
6. Calibration / quick check.
7. Session report.

## Verification

For every change:

- Keep the app runnable from the repository root.
- Add or update simple tests when changing core logic.
- Do not break the mock-data mode.
- Preserve protocol logs in JSONL format for later replay.
