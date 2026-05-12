# GAME_COMMUNICATION_PROTOCOL

## 1. 协议目标
- 主程序与小游戏强解耦。
- 游戏只通过 Runtime API 收发消息。
- 游戏禁止直接访问设备、DataCenter 内部对象、SQLite、CalibrationManager、SessionManager、StateMachine。

## 2. 消息类型
- RuntimeSnapshotView
- RuntimeCommand
- GameEvent

## 3. RuntimeSnapshotView 字段
schema_version, session_id, now_ms, user_id, game_id, attention, attention_age_ms, attention_fresh, gyro_x, gyro_y, gyro_z, gyro_age_ms, gyro_fresh, sqi, quality_state, fi_raw, fi_smoothed, fi_valid, fi_confidence, control_state, control_state_reason, warning_flags, error_flags。

## 4/5. RuntimeCommand
字段：schema_version, command_id, session_id, game_id, command_type, issued_at_ms, payload。
允许类型：start_game, pause_game, resume_game, stop_game, set_difficulty, set_feedback_mode。

## 6/7. GameEvent
字段：schema_version, event_id, session_id, game_id, event_type, created_at_ms, payload。
允许类型：score_update, behavior_sample, difficulty_request, game_completed, game_error, user_action。

## 8-13. payload 标准
- behavior_sample: window_ms, target_count, correct_count, omission_count, false_action_count, action_count, rt_samples_ms, accuracy, omission, false_action, rt_stability
- score_update: score, score_delta, combo, level
- difficulty_request: requested_level, reason, confidence
- game_completed: reason, final_score, user_finished
- game_error: code, message, recoverable
- user_action: action_type, target_id, success, rt_ms

## 14. 权限边界
- 小游戏只能发 difficulty_request，不能直接改难度。
- 小游戏只能发 game_completed，不能直接结束 session。

## 15. JSON 示例
```json
{"schema_version":"runtime.v1","session_id":"session_demo_20260512_120000","now_ms":123456,"user_id":"demo","game_id":"fake_game","attention":70,"attention_age_ms":80,"attention_fresh":true,"gyro_x":0.1,"gyro_y":0.2,"gyro_z":0.0,"gyro_age_ms":20,"gyro_fresh":true,"sqi":0.9,"quality_state":"ok","fi_raw":0.6,"fi_smoothed":0.58,"fi_valid":true,"fi_confidence":0.8,"control_state":"READY","control_state_reason":"stable","warning_flags":[],"error_flags":[]}
```
```json
{"schema_version":"runtime.v1","command_id":"cmd_001","session_id":"session_demo_20260512_120000","game_id":"fake_game","command_type":"start_game","issued_at_ms":123456,"payload":{}}
```
```json
{"schema_version":"runtime.v1","event_id":"evt_001","session_id":"session_demo_20260512_120000","game_id":"fake_game","event_type":"behavior_sample","created_at_ms":123999,"payload":{"window_ms":1000,"target_count":10,"correct_count":8,"omission_count":1,"false_action_count":1,"action_count":9,"rt_samples_ms":[320,410],"accuracy":0.8,"omission":0.1,"false_action":0.1,"rt_stability":0.7}}
```
```json
{"schema_version":"runtime.v1","event_id":"evt_010","session_id":"session_demo_20260512_120000","game_id":"fake_game","event_type":"game_completed","created_at_ms":133000,"payload":{"reason":"user_finish","final_score":123,"user_finished":true}}
```

## 16. 版本策略
- schema_version 当前定义为 `runtime.v1`。
- 破坏性变更必须升级 schema_version。
- 旧日志按当时 schema_version 解释。

## 17. 与 Task7 的关系
- SessionManager 只记录 RuntimeSnapshotView / GameEvent。
- SessionManager 不依赖具体游戏类。
- 日志写入 logs/sessions。
- SQLite 只保存摘要。

## 18. 与 Task8 的关系
- FakeGame 及后续 Pygame/WebSocket 版本必须遵守本协议。
