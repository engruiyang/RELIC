# SESSION_LOGGING

- Task7 目标：记录训练会话 JSONL 与 SQLite 摘要，不重算 FI。
- `logs/sessions/` 是正式训练日志；`logs/task6b/` 仅用于 Task6B 采集/调参。
- JSONL 每行：`ts`, `event_type`, `session_id`, `payload`。
- `training_sessions` 保存摘要字段（时长、tick、FI/SQI统计、GameEvent统计等）。
- `quality_state_duration_summary` 按 quality_state 累计时长。
- `control_state_duration_summary` 按 control_state 累计时长。
- `warning_duration_ms` 与 `unreliable_duration_ms` 可重叠（语义维度不同）。
- GameEvent 通过 `SessionManager.record_game_event` 入日志，且只接受标准 `GameEvent`。
- CLI:
  - `python -m ui_cli.run_session_debug --mode demo --duration-sec 10`
  - `python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_local.db`
  - `python -m ui_cli.run_session_debug --show-session SESSION_ID --db-path data/relic_local.db`
  - `python -m ui_cli.run_session_debug --show-log-path SESSION_ID --db-path data/relic_local.db`
- Task7 不负责真实游戏规则，仅记录协议消息。
