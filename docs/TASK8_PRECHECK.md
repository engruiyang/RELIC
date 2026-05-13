# TASK8_PRECHECK

## 必须通过的测试命令
```bash
pytest -q tests/test_runtime_contract.py tests/test_session_manager.py tests/test_task6_focus_estimator.py tests/test_task6_quality_gate.py tests/test_run_core_debug_user_context.py tests/test_calibration_manager.py tests/test_calibration_cli_management.py
```

## 必须可执行的 CLI
```bash
python -m ui_cli.run_session_debug --mode demo --duration-sec 1 --user-id demo_user --db-path data/relic_task7b.db
python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_task7b.db
python -m ui_cli.run_session_debug --show-session <SESSION_ID> --db-path data/relic_task7b.db
```

## Task8 前检查清单
1. `logs/sessions/` 可写。
2. `logs/task6b/` 未被 session 日志污染。
3. `GAME_COMMUNICATION_PROTOCOL.md` 已包含 RuntimeSnapshotView / RuntimeCommand / GameEvent。
4. `SESSION_LOGGING.md` 已说明 JSONL 与 SQLite 的职责。
5. Task6B 调参数据与 session 数据分开。
6. GameEvent `behavior_sample` schema 已明确。
7. SessionManager 只依赖标准 GameEvent，不依赖具体游戏类。
8. `COMMANDS.md` 没有被重写，只追加索引。

## Task8A 新增验证
```bash
pytest -q tests/test_game_manager.py tests/test_fake_game_client.py tests/test_task8_game_flow.py
python -m ui_cli.run_game_debug --mode demo --duration-sec 5 --user-id demo_user --db-path data/relic_task8a.db
```
