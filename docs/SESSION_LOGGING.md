# SESSION_LOGGING

## 1. 日志分层
- `logs/sessions/`：正式训练 session 日志（Task7+）。
- `logs/task6b/`：仅用于 Task6B 数据采集、标注与调参。
- 两者职责不同，不得混用。

## 2. JSONL 行格式
Session JSONL 每行是一个事件对象，核心字段：
- `ts`：写入时间戳（ISO8601）
- `event_type`：事件类型
- `session_id`：会话 ID
- `payload`：事件数据（JSON）

## 3. 常见事件示例
- `session_start`：记录 user_id/game_id/started_at 等。
- `runtime_snapshot`：记录 RuntimeSnapshotView 快照（高频）。
- `game_event`：记录标准 GameEvent（score_update / behavior_sample 等）。
- `session_summary`：记录本次统计摘要（与 DB 摘要一致）。
- `session_end`：记录结束状态、结束时间、收尾信息。

## 4. SQLite `training_sessions` 字段说明
摘要表按 session 维度保存低频统计，不保存高频原始快照。
典型字段包括：
- 身份与时间：`session_id`, `user_id`, `game_id`, `started_at`, `ended_at`, `status`
- 时长：`duration_ms`, `warning_duration_ms`, `unreliable_duration_ms`
- FI/SQI：`final_fi_avg`, `final_sqi_avg`, `fi_min`, `fi_max`, `fi_last`, `sqi_min`, `sqi_max`, `sqi_last`
- GameEvent 统计：`game_event_count`, `behavior_sample_count`, `score_update_count`, `difficulty_request_count`, `game_error_count`, `user_action_count` 等
- 汇总 JSON：`quality_state_duration_summary`, `control_state_duration_summary`

## 5. duration 语义
- `duration_ms` 是会话总时长。
- `warning_duration_ms` 与 `unreliable_duration_ms` 可重叠：
  - warning 表示告警维度
  - unreliable 表示可靠性维度
  - 同一时间段可同时满足两类条件。

## 6. SessionManager 职责边界
- SessionManager 只记录与聚合，不重新计算 FI/SQI。
- FI/SQI 来源于 RuntimeSnapshotView（Task6B 估计层）。
- SessionManager 仅依赖标准 GameEvent，不依赖具体游戏类。

## 7. CLI 用法
```bash
python -m ui_cli.run_session_debug --mode demo --duration-sec 1 --user-id demo_user --db-path data/relic_task7b_cleanup.db
python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_task7b_cleanup.db
python -m ui_cli.run_session_debug --show-session <SESSION_ID> --db-path data/relic_task7b_cleanup.db
python -m ui_cli.run_session_debug --show-log-path <SESSION_ID> --db-path data/relic_task7b_cleanup.db
```

## 8. 存储策略总结
- JSONL：高频、可回放、保留事件细节。
- SQLite：低频摘要、便于检索与统计。
- SQLite 不保存高频 snapshot 原文，避免体积膨胀与职责混淆。
