# TASK23A GUI Command Registry

- 目标：建立统一 command registry，按页面和类别暴露 active commands 到 GUI。
- 命名：`<domain>.<action>`，例如 `user.load`、`calibration.status`、`training.start_session`。
- page_id：`home/user/calibration/runtime/training/game/report/diagnostics/developer_lab`。
- execution_mode：
  - `native`：可走 `guiBridge.invokeAction`
  - `manual`：人工执行
  - `copy_only`：仅展示命令卡和 CLI 参考
  - `disabled`：当前不可执行
- status：`active/native_ready/manual/copy_only/planned/unknown/deprecated/not_implemented`。
- danger_level：`safe/normal/writes_db/connects_live/generates_files/advanced/destructive`。
- 产品命令与开发命令：产品命令优先 native；开发命令进 Developer Lab，避免普通用户误触危险链路。
- GUI 不通过 subprocess 执行 CLI：保持 bridge-only 边界、避免平台注入风险、避免 UI 卡死。
- 页面覆盖：
  - User: user.*
  - Calibration: calibration.*
  - Training/Game: training.* + game.status
  - Report: report.*
  - Diagnostics: runtime.* + diagnostics.*
  - Developer Lab: game.debug_* + developer.task6b_*
- 后续：TASK23B/C/D 复用 registry，将 native_ready 持续迁移为 native。

## TASK23A2 UI usage update
- TASK23A2: page-level Action Panel + Page Feedback wired to pageCommandManifestJson.
