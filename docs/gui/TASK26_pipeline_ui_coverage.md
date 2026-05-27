# TASK26 Pipeline UI Coverage 草案（TASK26A）

## 1. Pipeline UI Coverage 的目的
- 防止卡片自由编辑后核心管线入口消失。
- 防止 `live.safe_stop` 被删除。
- 防止 attention / gyro 新鲜度字段不可见。
- 防止 warning / error 没有诊断入口。
- 防止 action_id 拼写错误导致按钮失效。

## 2. mandatory pipeline 与 optional pipeline

### mandatory
- `live_connection`
- `runtime`
- `attention_stream`
- `gyro_stream`
- `session`
- `training`
- `calibration`
- `diagnostics`

### optional
- `report`
- `user`
- `game`
- `decoration`

## 3. 核心 pipeline 建议覆盖

### live_connection
- required_fields: `appState.connection_status`, `runtimeSnapshot.device_connected`
- required_buttons: `app.refresh_now`（或实际刷新/重连 action_id）, `live.safe_stop`
- required_cards: `runtime_io_card` 或 `connection_status_card`

### runtime
- required_fields: `runtimeSnapshot.stream_alive`, `runtimeSnapshot.warning_flags`, `runtimeSnapshot.error_flags`
- required_cards: `runtime_io_card`, `diagnostics_summary_card`

### attention_stream
- required_fields: `runtimeSnapshot.attention`, `runtimeSnapshot.attention_age_ms`
- required_cards: `attention_stream_card` 或 `runtime_io_card`

### gyro_stream
- required_fields: `runtimeSnapshot.gyro_x`, `runtimeSnapshot.gyro_y`, `runtimeSnapshot.gyro_z`, `runtimeSnapshot.gyro_age_ms`
- required_cards: `gyro_stream_card` 或 `runtime_io_card`

### session
- required_fields: `sessionState.session_active`, `sessionState.current_session_id`, `sessionState.session_elapsed_ms`
- required_buttons: `session.start`, `session.stop`（或仓库真实 action_id）
- required_cards: `session_card`, `training_control_card`

### training
- required_fields: `controlState.current_session_id`（或仓库真实训练状态字段）
- required_buttons: `session.start`, `session.stop`, `live.safe_stop`（或仓库真实 action_id）
- required_cards: `training_control_card`

### calibration
- required_fields: calibration status 相关真实字段
- required_buttons: `calibration.status`, `calibration.start`, `calibration.cancel`（或仓库真实 action_id）
- required_cards: `calibration_status_card`, `calibration_action_card`

### diagnostics
- required_fields: `warning_flags`, `error_flags`, `last_error`
- required_buttons: `diagnostics.refresh`（或仓库真实 action_id）
- required_cards: `diagnostics_summary_card`

## 4. live.safe_stop 策略
- `live.safe_stop` 必须 **always accessible**。
- 不能只放在 `DeveloperLab`。
- 至少应出现在 `dock`、`status_bar`、`training_control_card` 三者之一。
- 后续测试应检查该 action_id 是否存在并可见。

## 5. 缺失处理策略

### 开发模式
- coverage 测试失败。
- 输出缺失的 pipeline / card / field / button 列表。

### 运行模式（后续阶段）
- 可注入 fallback card。
- 显示 warning。
- 此策略不在 TASK26A 实现。

## 备注
- 部分字段命名需在 TASK26C 对照 `guiBridge` 实际字段做 schema checker 校验。
