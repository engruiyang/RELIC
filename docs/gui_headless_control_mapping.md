# GUI Headless Control Mapping (TASK21-C)

## 目标
将无头能力通过稳定 action_id 映射到最小 GUI 控制台，不新增并行业务链路。

## Action Contract
核心 action_id：
- app.refresh_now, app.quit, live.reconnect, live.safe_stop
- user.ensure_demo, user.show_profile
- calibration.start, calibration.status
- session.start, session.stop, session.status
- game.status
- diagnostics.clear_last_error, diagnostics.refresh

## 后端来源
QML -> `GuiBridge.invokeAction` -> `GuiFacade.invoke_action` -> 既有 `handle_gui_command` / source 能力。
不通过 subprocess 调用 ui_cli。

## 模式支持概览
- mock: refresh/quit/user/session/status 支持；reconnect 通常 unsupported；safe_stop 为 no-op/unsupported 但可回显。
- core: 只读，危险操作返回 `readonly_not_allowed`。
- core-control: 类 mock+core control。
- live-readonly: refresh/reconnect 支持；危险操作 `readonly_not_allowed`。
- live-control: refresh/reconnect 可用；session start/stop 映射到 live-control source；safe_stop 若后端无能力返回 unsupported/noop。

## controlManifestJson 字段
- action_id, label, category, enabled, supported, readonly_allowed, live_control_required, description

## controlStateJson 字段
- mode, control_enabled, readonly
- current_user_id/current_session_id/current_game_id
- session_active, calibration_active, live_connected
- last_command, last_command_result, last_command_error, command_count
- latest_report_path, app_elapsed_ms, session_elapsed_ms

## duration_ms / elapsed 语义
- duration_ms：动作/任务约束时长，不是 GUI uptime。
- app_elapsed_ms：GUI 进程启动后运行时长（由 facade+Qt pump持续刷新）。
- session_elapsed_ms：仅 session_active 时刷新，否则 n/a。

## 美工自定义边界
- 可改布局/颜色/文案/分组。
- 不要改 action_id。
- 不要绕过 guiBridge。
- 不要让 QML 访问 DataCenter/DeviceManager/PlatformGateway/raw stream。

## 非目标
不包含页面切换、GameCanvas、素材系统、正式训练页。


## 定位说明
- MinimalGui 是 **Developer Diagnostics Console**，不是最终正式 GUI 页面。
- TASK21-C3 验收用户优先使用 `TEST`（`--user-id TEST --db-path data/relic_local.db`）。
- `demo` / `ensure_demo_user` 仅作为 debug fallback。

## Show Profile 反馈字段
`user.show_profile` 返回结构化字段：
- 无用户：`missing_user`
- 用户不存在：`user_not_found`
- profile 不存在：`profile_not_found`
- 有 profile：`current_user_id`, `user_type`, `profile_loaded`, `last_calibration_id`, `attention_low_threshold`, `attention_high_threshold`, `preferred_game_id`, `difficulty_level`

## Session 控制状态字段
`controlStateJson` 至少包含：
- `session_active`
- `current_session_id`
- `session_elapsed_ms`
- `latest_report_path`
- `last_session_status`

## Calibration 语义
- `calibration.start`: 当前仍为 `not_implemented`（需后续完整 Calibration 页面任务实现 user/source/type/progress/failure UI）。
- `calibration.status`: 只读查询，返回 `missing_user` / `no_calibration` / `profile_without_calibration` / `accepted`，并在有绑定时返回 `last_calibration_id`, `calibration_usable`, `latest_valid`, `failure_reason`, `source`, `attention_baseline`, `gyro_noise_rms`。

## 配色说明
本轮仅做可读性修复（高对比诊断风格），不是完整主题系统。
