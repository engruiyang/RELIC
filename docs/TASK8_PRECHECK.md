# TASK8_PRECHECK

## Mandatory test gate
Run and pass:

```bash
pytest -q tests/test_runtime_contract.py tests/test_session_manager.py tests/test_task6_focus_estimator.py tests/test_task6_quality_gate.py tests/test_run_core_debug_user_context.py tests/test_calibration_manager.py tests/test_calibration_cli_management.py
```

## Mandatory CLI gate
Run and validate:

```bash
python -m ui_cli.run_session_debug --mode demo --duration-sec 1 --user-id demo_user --db-path data/relic_task7b.db
python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_task7b.db
python -m ui_cli.run_session_debug --show-session <SESSION_ID> --db-path data/relic_task7b.db
```

## Must-confirm checklist
1. `logs/sessions/` is writable.
2. `logs/task6b/` is not polluted by session logs.
3. `GAME_COMMUNICATION_PROTOCOL.md` includes RuntimeSnapshotView / RuntimeCommand / GameEvent.
4. `SESSION_LOGGING.md` clearly separates JSONL responsibility vs SQLite responsibility.
5. Task6B tuning data and training-session data are separated.
6. GameEvent `behavior_sample` schema is documented.
7. SessionManager depends only on standard `GameEvent`, not concrete game classes.
