# COMMANDS

> 本文档只记录仓库中可确认来源的命令。凡是未在代码/文档中确认的命令，不标记为 active。

## 测试命令

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `python -m pytest -q` | 运行全量/默认测试 | `tests/` | 否（测试内可能使用临时 DB） | 否 | 否 | `passed`, `failed` | active |
| `python -m pytest -q tests/test_calibration_manager.py tests/test_user_cli_management.py tests/test_user_debug_cli.py tests/test_user_profile_storage.py tests/test_task2_mock_data_center.py tests/test_platform_gateway_messages.py tests/test_ui_cli_data_center_flow.py` | Task5 回归测试集合 | `tests/*.py` | 部分测试会写临时 SQLite | 否 | 否 | `N passed` | active |

## Core / DataCenter 调试命令

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `python -m ui_cli.run_core_debug --bridge mock` | 本地 mock 数据流调试 | `ui_cli/run_core_debug.py` | 否 | 否 | 否 | `tick`, `attention`, `gyro`, `quality`, `error_flags` | active |
| `python -m ui_cli.run_core_debug --bridge live --host 127.0.0.1 --port 8000` | live 桥接调试 | `ui_cli/run_core_debug.py` | 否 | 是 | 否 | `connected`, `stream_alive`, `attention_fresh` | active |
| `python -m ui_cli.run_core_debug --bridge live --mode user --user-id TEST` | live 桥接 + 指定用户上下文调试 QualityGate | `ui_cli/run_core_debug.py` | 否（仅读） | 是 | 否 | `current_user_id`, `profile.last_calibration_id`, `formal_training_allowed` | active |
| `python -m ui_cli.run_core_debug --bridge mock --mode demo` | mock 桥接 + demo 用户上下文调试 QualityGate | `ui_cli/run_core_debug.py` | 否（仅读） | 否 | 否 | `bound_calibration_source`, `calibration_usable`, `quality_reasons` | active |
| `python -m main` | 启动 AppController 主流程 | `main.py` | 可能（依配置） | 依配置 | 依模块 | 控制台 state/debug 输出 | unknown |

## Platform / live 调试命令

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `python -m ui_cli.run_core_debug --bridge live --host 127.0.0.1 --port 8000 --ticks 20 --interval 0.5` | 验证 live IPC 输入链路 | `ui_cli/run_core_debug.py` | 否 | 是 | 否 | `connected`, `alive`, `quality_reasons` | active |

## 用户与 Profile 命令

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `python -m ui_cli.run_user_debug --mode demo` | 加载/创建 demo 用户并打印 profile | `ui_cli/run_user_debug.py` | 是 | 否 | 否 | `current_user_id`, `user_type`, `profile.last_calibration_id` | active |
| `python -m ui_cli.run_user_debug --mode guest` | 进入 guest 模式（通常不落库） | `ui_cli/run_user_debug.py` | 否（users/profile 不写入） | 否 | 否 | `current_user_id=guest`, `persisted=False` | active |
| `python -m ui_cli.run_user_debug --mode user --user-id TEST` | 加载指定本地用户 | `ui_cli/run_user_debug.py` | 是（登录时间/profile） | 否 | 否 | `current_user_id`, `profile_loaded` | active |
| `python -m ui_cli.run_user_debug --list-users` | 列出已保存用户 | `ui_cli/run_user_debug.py` | 否 | 否 | 否 | `user_count`, `user_id`, `user_type` | active |
| `python -m ui_cli.run_user_debug --create-user TEST --display-name "Test"` | 创建本地用户（不存在时） | `ui_cli/run_user_debug.py` | 是 | 否 | 否 | `create_user_result`, `current_user_id` | active |

## 校准命令

- `--source mock`：开发/测试用 mock 校准。
- `--source ipc`：真实平台 IPC 数据校准，要求平台已启动、端口正确并进入范式页面。
- `--source ipc` 无数据会失败，不会自动回退到 mock。
- `--source ipc` 在校准中若发生平台断开，会以 `ipc_stream_interrupted` / `live_stream_disconnected` 失败。
- mock 校准结果不能作为真实注意力基线。
- 真实 attention 基线至少需要 8 秒采样窗口。
- 普通 CLI 会在每个校准阶段开始前实时输出提示（title / user_instruction / avoid_instruction / duration_hint）。
- `failure_reason` 是按失败类型分类，不要求把所有 IPC 异常都归为 `ipc_stream_interrupted`。

### 校准失败原因语义（Task5）

- 连接类失败（仅在明确捕获 socket/bridge/receiver 断开事件时使用）：
  - `ipc_stream_interrupted`
  - `live_stream_disconnected`
- 样本不足类失败（连接未明确断开，但窗口内有效样本不够）：
  - `insufficient_valid_samples`
- 注意力质量类失败（有 attention 数据，但质量或更新不足）：
  - `attention_update_too_sparse`
  - `attention_missing` / `attention_lost`（按实现语义）

所有失败原因都满足以下约束：
- `valid=False`
- `persisted=False`
- 不更新 `profile.last_calibration_id`
- `source=ipc` 失败时不 fallback 到 `mock`

用户恢复建议（按 failure_reason）：
- `ipc_stream_interrupted` / `live_stream_disconnected`：检查平台是否仍在推流、端口是否正确、桥接进程/接收线程是否退出后重连重试。
- `insufficient_valid_samples`：延长稳定采样时间、保持头部静止、确认佩戴贴合后重试。
- `attention_update_too_sparse`：确认注意力值在窗口内持续更新，减少干扰动作并重试。

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `python -m ui_cli.run_calibration_debug --action status --mode user --user-id TEST` | 查看当前用户校准绑定/最新状态 | `ui_cli/run_calibration_debug.py` | 否（仅读） | 否 | 否 | `profile.last_calibration_id`, `latest_calibration_id`, `latest_valid` | active |
| `python -m ui_cli.run_calibration_debug --action start --mode demo --calibration-type auto` | 执行校准（默认显示阶段/进度） | `ui_cli/run_calibration_debug.py` | demo/user: 是；guest: 否 | 否 | 否 | `calibration_id`, `calibration_type`, `valid`, `failure_reason` | active |
| `python -m ui_cli.run_calibration_debug --action cancel --mode user --user-id TEST` | 取消校准（当前实现为同步取消记录返回） | `ui_cli/run_calibration_debug.py` | 否（不绑定） | 否 | 否 | `valid=False`, `failure_reason=cancelled_by_user` | active |
| `python -m ui_cli.run_calibration_debug --action list --mode user --user-id TEST` | 列出用户历史校准 | `ui_cli/run_calibration_debug.py` | 否（仅读） | 否 | 否 | `calibration_count`, `calibrations[]` | active |
| `python -m ui_cli.run_calibration_debug --action latest --mode user --user-id TEST` | 读取用户最新校准 | `ui_cli/run_calibration_debug.py` | 否（仅读） | 否 | 否 | `calibration_id`, `valid`, `failure_reason` | active |
| `python -m ui_cli.run_calibration_debug --action show --calibration-id cal_xxx` | 读取指定 calibration 详情 | `ui_cli/run_calibration_debug.py` | 否（仅读） | 否 | 否 | `attention_baseline`, `gyro_noise_rms`, `signal_quality_baseline` | active |
| `python -m ui_cli.run_calibration_debug --action bind --mode user --user-id TEST --calibration-id cal_xxx` | 绑定有效 calibration 到 profile | `ui_cli/run_calibration_debug.py` | 是（更新 `user_profiles.last_calibration_id`） | 否 | 否 | `old_last_calibration_id`, `new_last_calibration_id` | active |
| `python -m ui_cli.run_calibration_debug --action start --mode user --user-id TEST --verbose-events` | 输出完整 events 列表（调试，人类可读） | `ui_cli/run_calibration_debug.py` | demo/user: 是；guest: 否 | 否 | 否 | `events=[...]` | active |
| `python -m ui_cli.run_calibration_debug --action start --mode user --user-id TEST --json-events` | 以结构化事件输出（调试） | `ui_cli/run_calibration_debug.py` | demo/user: 是；guest: 否 | 否 | 否 | `events=[...]` | active |
| `python -m ui_cli.run_calibration_debug --action start --mode user --user-id TEST --fast` | fast 模式（测试/开发快速完成） | `ui_cli/run_calibration_debug.py` | demo/user: 是；guest: 否 | 否 | 否 | `events`, `valid`, `calibration_id` | active |
| `python -m ui_cli.run_calibration_debug --action start --mode user --user-id TEST --no-progress` | 关闭进度行输出，仅保留结果 | `ui_cli/run_calibration_debug.py` | demo/user: 是；guest: 否 | 否 | 否 | `valid`, `calibration_id` | active |


## Task6B 调参与评估命令（mock + 真实）

> 以下命令覆盖 Task6B 的完整调参链路：录制数据 → 标注 → 评估 → 搜参。

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `bash scripts/task6b_record.sh mock demo 180 baseline` | 使用 mock 数据录制 Task6B 样本（demo 上下文） | `scripts/task6b_record.sh` / `ui_cli/run_core_debug.py` | 否 | 否 | `logs/task6b/*.jsonl`, `labels/task6b/*.yaml`, `labels/task6b/*.frames.csv` | `session_id`, `quality`, `focus_index`, `control_state` | active |
| `bash scripts/task6b_record.sh live TEST 180 real_trial` | 使用真实 IPC 数据录制 Task6B 样本（local user） | `scripts/task6b_record.sh` / `ui_cli/run_core_debug.py` | 否（仅读 profile） | 是（默认 `127.0.0.1:8000`） | `logs/task6b/*.jsonl`, `labels/task6b/*.yaml`, `labels/task6b/*.frames.csv` | `connected`, `stream_alive`, `quality_reasons` | active |
| `bash scripts/task6b_record.sh mock demo 180 baseline --frame-sec 2` | mock 录制并设置标注窗口长度 | `scripts/task6b_record.sh` / `ui_cli/run_core_debug.py` | 否 | 否 | 同上 | `frame_start_ms`, `frame_end_ms` | active |
| `python -m ui_cli.evaluate_task6b --input "logs/task6b/*.jsonl" --labels "labels/task6b/*.frames.csv" --config config/task6b.yaml --out reports/task6b_eval.json` | 对已标注样本做离线评估 | `ui_cli/evaluate_task6b.py` | 否 | 否 | `reports/task6b_eval.json` | `frame_accuracy`, `macro_f1`, `confusion_matrix`, `score` | active |
| `bash scripts/task6b_eval.sh` | 评估脚本快捷入口（默认路径） | `scripts/task6b_eval.sh` / `ui_cli/evaluate_task6b.py` | 否 | 否 | `reports/task6b_eval.json` | `overall`, `per_session` | active |
| `python -m ui_cli.tune_task6b --input "logs/task6b/*.jsonl" --labels "labels/task6b/*.frames.csv" --base-config config/task6b.yaml --trials 300 --method random --seed 42 --out config/task6b_tuned_candidates.json --report reports/task6b_tune_report.json` | 对 Task6B 参数做随机搜索调参 | `ui_cli/tune_task6b.py` | 否 | 否 | `config/task6b_tuned_candidates.json`, `reports/task6b_tune_report.json` | `top_candidates`, `score`, `macro_f1`, `validation` | active |
| `bash scripts/task6b_tune.sh` | 调参脚本快捷入口（`TASK6B_TRIALS` 可覆盖 trials） | `scripts/task6b_tune.sh` / `ui_cli/tune_task6b.py` | 否 | 否 | `config/task6b_tuned_candidates.json`, `reports/task6b_tune_report.json` | `top_candidates` | active |

### Task6B 实操建议

- **mock 调参流程**：`task6b_record.sh mock` → 人工编辑 `labels/task6b/*.frames.csv` → `task6b_eval.sh` → `task6b_tune.sh`。
- **真实调参流程**：确认平台推流后执行 `task6b_record.sh live`，再执行相同评估/调参步骤。
- `task6b_record.sh` 参数：`<bridge> <user_id> <duration_sec> <tag>`，其中 `bridge` 仅支持 `mock` 或 `live`。
- 真实录制建议使用 `--mode user` 对应的有效本地用户 ID，避免使用 guest。

## 后续 planned 命令

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `python -m ui_cli.run_session_debug ...` | 训练 Session 调试（Task7 规划） | 未实现（仅目录规划 `session/`） | TBD | TBD | TBD | TBD | planned |
| `python -m runtime.* ...` | Runtime API 调试（Task8 规划） | 未实现完整 CLI（仅 `runtime/` 目录） | TBD | TBD | TBD | TBD | planned |
| `python -m game.* ...` | 游戏管理调试（Task8 规划） | 未实现完整 CLI（仅 `game/` 目录） | TBD | TBD | TBD | TBD | planned |

## deprecated 历史命令

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `python -m relic_core.*` | 历史路径命令集合（冻结） | `relic_core/`（历史兼容） | unknown | unknown | unknown | unknown | deprecated |
| `python -m games.*` | 历史游戏原型路径命令集合 | `games/`（历史兼容） | unknown | unknown | unknown | unknown | deprecated |

## unknown 命令说明

- `python -m main` 被标记为 `unknown`：入口存在，但 README/docs 未提供稳定参数契约与运行前置条件说明；因此不把它作为稳定 debug 命令宣传。


- 默认校准（first_profile / quick_check）只要求静止和平视，不需要摆头动作。
- `--mode user` 必须配合 `--user-id`。

- 普通模式适合人类查看；`--json-events` / `--verbose-events` 适合 GUI 或调试工具读取事件。
- `--calibration-type` 仅支持：auto / first_profile / quick_check / periodic / triggered。
- `calibration_id` 示例中的尖括号仅为占位符，实际命令不要输入尖括号。

- `--calibration-type` 仅支持 auto / first_profile / quick_check / periodic / triggered。
- `calibration_id` 示例中的尖括号仅为占位符，请替换为真实 ID。

- demo 模式不能带 `--user-id`；local 用户必须使用 `--mode user --user-id <ID>`。
- IPC 推荐命令：`python -m ui_cli.run_calibration_debug --action start --mode user --user-id TEST --source ipc`。
- `--host/--port` 省略时自动使用默认 `127.0.0.1:8000`，显式传参会覆盖默认。

- demo 模式不能带 `--user-id`；local 用户必须使用 `--mode user --user-id <ID>`。
- local_user 默认 source=ipc；demo 默认 source=mock。
- IPC 推荐：`python -m ui_cli.run_calibration_debug --action start --mode user --user-id TEST --source ipc`。
- source=ipc 默认使用配置中的 `127.0.0.1:8000`，无数据/断流不会 fallback 到 mock。
- 如需只读检查绑定一致性：`--action validate-bindings`。

## Task6B / Runtime / Session 命令补充

更多命令见：
- docs/COMMANDS_TASK6B_RUNTIME_SESSION.md

## Task7 / Task8 命令补充

更多命令见：
- docs/COMMANDS_TASK6B_RUNTIME_SESSION.md
- docs/TASK8_LIVE_GAME_PIPELINE.md

| 命令 | 用途 | 入口文件 | 写数据库 | 连接平台 | 生成文件 | 典型输出字段 | 状态 |
|---|---|---|---|---|---|---|---|
| `python -m ui_cli.run_session_debug --mode demo --duration-sec 1 --user-id demo_user --db-path data/relic_task7b.db` | Task7 session 最小闭环验证 | `ui_cli/run_session_debug.py` | 是（SQLite summary） | 否 | `logs/sessions/*.jsonl` | `session_id`, `game_event_count` | active |
| `python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_task7b.db` | Task7 session 列表查询 | `ui_cli/run_session_debug.py` | 否（仅读） | 否 | 否 | `session_id`, `status`, `score` | active |
| `python -m ui_cli.run_session_debug --show-session <SESSION_ID> --db-path data/relic_task7b.db` | Task7 session 摘要查询 | `ui_cli/run_session_debug.py` | 否（仅读） | 否 | 否 | `behavior_sample_count`, `game_event_count` | active |
| `python -m ui_cli.run_game_debug --bridge mock --mode demo --duration-sec 5 --user-id demo_user --db-path data/relic_task8c_mock.db --game-id fake_game --print-jsonl` | Task8C mock 双向 pipeline 验证 | `ui_cli/run_game_debug.py` | 是（SQLite summary） | 否 | `logs/sessions/*.jsonl`, `logs/game_debug/*.pipeline.jsonl` | `tick`, `event_types`, `view_state` | active |
| `python -m ui_cli.run_game_debug --bridge live --mode user --user-id TEST --host 127.0.0.1 --port 8000 --duration-sec 60 --db-path data/relic_local.db --game-id fake_game --print-jsonl` | Task8C live 双向 pipeline 验证 | `ui_cli/run_game_debug.py` | 是（SQLite summary） | 是 | `logs/sessions/*.jsonl`, `logs/game_debug/*.pipeline.jsonl` | `tick`, `sqi`, `fi_smoothed`, `event_types` | active |
| `python -m ui_cli.run_game_debug --bridge live --mode user --user-id TEST --host 127.0.0.1 --port 8000 --duration-sec 60 --db-path data/relic_local.db --game-id fake_game --record-pipeline-jsonl logs/game_debug/live_TEST_pipeline.jsonl` | Task8C live pipeline JSONL 落盘 | `ui_cli/run_game_debug.py` | 是（SQLite summary） | 是 | `logs/game_debug/live_TEST_pipeline.jsonl` | `input`, `output`, `warnings`, `errors` | active |

# Task8 Runtime/Game Pipeline Commands

## Task8 scope
Task8 仅覆盖以下范围：
- Runtime API
- GameManager
- FakeGame
- GameViewState
- mock pipeline
- live pipeline
- Task6B calibrated config 接入

以下内容不属于 Task8（属于后续 Task9）：
- PlatformReporter
- ReplayAdapter
- 官方报告上传
- 鼠标事件兼容层

## Regression tests
```powershell
pytest -q `
  tests/test_runtime_contract.py `
  tests/test_session_manager.py `
  tests/test_task6_focus_estimator.py `
  tests/test_task6_quality_gate.py `
  tests/test_run_core_debug_user_context.py `
  tests/test_game_manager.py `
  tests/test_task8_game_flow.py
```

## Check CLI options
```powershell
python -m ui_cli.run_game_debug -h
```
应能看到：
- `--task6b-config`
- `--record-pipeline-jsonl`
- `--print-jsonl`
- `--bridge {mock,live}`

## Mock game pipeline smoke test
```powershell
python -m ui_cli.run_game_debug `
  --mode user `
  --bridge mock `
  --duration-sec 5 `
  --user-id TEST `
  --db-path data/relic_local.db `
  --game-id fake_game `
  --task6b-config config/task6b_grid_calibrated.yaml `
  --print-jsonl `
  --record-pipeline-jsonl logs/sessions/task8c_mock_calibrated_pipeline.jsonl
```
预期：
- `task6b_config_loaded=true`
- `game_event_count > 0`
- `view_state` 出现
- `behavior_sample_count` 可随 mock 输入产生

## Live 20s verification
```powershell
python -m ui_cli.run_game_debug `
  --mode user `
  --bridge live `
  --host 127.0.0.1 `
  --port 8000 `
  --duration-sec 20 `
  --user-id TEST `
  --db-path data/relic_local.db `
  --game-id fake_game `
  --task6b-config config/task6b_grid_calibrated.yaml `
  --print-jsonl `
  --record-pipeline-jsonl logs/sessions/task8c_live_calibrated_20s.jsonl
```
预期：
- `provider_fallback_used=false`
- `calibration_loaded=true`
- `calibration_usable=true`
- `estimation_allowed=true`
- `quality_state` 大部分为 `ok`
- `fi_valid=true` 出现
- `behavior_sample_count > 0`
- `score` 增长

## Live 60s verification
```powershell
python -m ui_cli.run_game_debug `
  --mode user `
  --bridge live `
  --host 127.0.0.1 `
  --port 8000 `
  --duration-sec 60 `
  --user-id TEST `
  --db-path data/relic_local.db `
  --game-id fake_game `
  --task6b-config config/task6b_grid_calibrated.yaml `
  --print-jsonl `
  --record-pipeline-jsonl logs/sessions/task8c_live_calibrated_60s.jsonl
```
预期：
- `tick_count` 接近 60
- `fallback_count=0`
- `fi_valid_count > 0`（理想接近 `tick_count`）
- `behavior_tick_count > 0`
- `score_last > 0`
- `quality_state` 不应长期 `error`
- `control_state` 不应全是 `UNRELIABLE_SIGNAL`

## Inspect 60s result
```powershell
python tools/inspect_task8c_live.py `
  logs/sessions/task8c_live_calibrated_60s.jsonl
```
输出至少包含：
- `tick_count`
- `quality_states`
- `control_states`
- `fallback_count`
- `calibration_loaded_count`
- `calibration_usable_count`
- `estimation_allowed_count`
- `fi_valid_count`
- `behavior_tick_count`
- `score_last`
- `Final Verdict`

## Common pitfalls
- live 测试必须使用含 TEST 用户和校准记录的 `data/relic_local.db`。
- 不要使用空的 `data/relic_task8c_live.db`，除非已经创建 TEST 用户并写入校准记录。
- 若出现 `user not found: TEST`，说明 `db_path` 不对或测试库没有用户。
- 若 `attention_fresh=true` 但 `quality_state` 长期 `error`，应检查 `provider_fallback_used`、`calibration_loaded`、`calibration_usable`、`estimation_allowed`。
- 若 `run_core_debug live` 正常但 `run_game_debug live` 异常，问题通常在 game live provider 到 RuntimeSnapshotView 的组装路径。
- 第 1 tick 出现 `attention_missing/gyro_missing` 是正常启动现象。
- 60s 内没有 `STABLE_FOCUS` 不一定失败；Task8 验收重点是 live pipeline 是否有效流动。

## Task8 acceptance checklist
- [ ] pytest regression passed
- [ ] run_game_debug -h includes --task6b-config
- [ ] mock pipeline runs
- [ ] live 20s runs
- [ ] live 60s runs
- [ ] fallback_count=0
- [ ] calibration_loaded_count>0
- [ ] estimation_allowed_count>0
- [ ] fi_valid_count>0
- [ ] behavior_tick_count>0
- [ ] score_last>0
- [ ] no long-term quality_state=error
- [ ] no all-UNRELIABLE_SIGNAL after startup
- [ ] GameViewState updates
