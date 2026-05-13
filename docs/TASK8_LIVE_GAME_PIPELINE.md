# TASK8_LIVE_GAME_PIPELINE

## Task8C 定位
Task8C 是双向 live game pipeline：
- 主系统 -> 游戏：`RuntimeSnapshotView`
- 游戏 -> 主系统：`GameEvent`
- CLI 输出/JSONL 只是观察镜像，不是私有协议。

## 双向链路
- 输入：live/mock snapshot dict -> RuntimeSnapshotView -> LocalRuntime.publish_snapshot -> GameManager -> FakeGameClient
- 输出：FakeGameClient -> GameEvent -> GameManager 校验 -> SessionManager.record_game_event -> logs/sessions + SQLite summary

## 日志路径
- `logs/task6b/`：仅 Task6B 采集/调参
- `logs/sessions/`：正式 session 日志
- `logs/game_debug/`：Task8C pipeline 调试 JSONL

## 命令示例
Mock:
```bash
python -m ui_cli.run_game_debug --bridge mock --mode demo --duration-sec 5 --user-id demo_user --db-path data/relic_task8c_mock.db --game-id fake_game --print-jsonl
```
Live:
```bash
python -m ui_cli.run_game_debug --bridge live --mode user --user-id TEST --host 127.0.0.1 --port 8000 --duration-sec 60 --db-path data/relic_local.db --game-id fake_game --print-jsonl
```
记录 pipeline:
```bash
python -m ui_cli.run_game_debug --bridge live --mode user --user-id TEST --host 127.0.0.1 --port 8000 --duration-sec 60 --db-path data/relic_local.db --game-id fake_game --record-pipeline-jsonl logs/game_debug/live_TEST_pipeline.jsonl
```

## 每 tick 字段
- input: attention/sqi/fi_smoothed/fi_valid/control_state/... 
- output: event_count/event_types/score_update_count/behavior_sample_count/difficulty_request_count/game_completed_count/score/combo/level
- view_state: `game_view.v1` 下当前 status/feedback 等

## 规则说明
- `UNRELIABLE_SIGNAL` 不输出有效 behavior_sample（避免把信号问题伪装成行为问题）。
- behavior_sample 当前仅记录到 SessionManager，暂不接入 FocusEstimator。
- `game_completed` 只作为事件，不直接结束 session。
- `difficulty_request` 只作为请求，不直接修改 profile。
- 后续 Task8D/Task6C 再讨论 S_B 正式接入。
