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
