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
- mock 校准结果不能作为真实注意力基线。
- 真实 attention 基线至少需要 8 秒采样窗口。

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
