# GUI Live Bus Status (TASK21)

## 目标

TASK21 的目标是在保持 QML smoke shell 稳定性的前提下，把真实运行状态总线字段进入 GUI，形成可信的 live bus status / diagnostics 面板。

## 数据来源（只读）

QML 仅通过 `guiBridge` 的以下只读属性读取状态：

- `guiBridge.appState`
- `guiBridge.runtimeSnapshot`
- `guiBridge.sessionState`
- `guiBridge.gameHudJson`

QML 不直接读取设备，不直接读取平台原始流，不绕过 bridge 访问底层 DataCenter / DeviceManager / PlatformGateway。

## 字段分组

- Connection: `connection_status`, `stream_alive`, `device_connected`
- Attention: `attention`, `attention_fresh`, `attention_age_ms`, `attention_last_update_ms`
- Gyroscope: `gyro_x`, `gyro_y`, `gyro_z`, `gyro_fresh`, `gyro_age_ms`, `gyro_last_update_ms`
- Session: `session_type`, `session_id`, `latest_report_path` (回退 `report_path`)
- Diagnostics: `warning_flags`, `error_flags`
- Game HUD: 现有 HUD 关键字段（缺失显示 `n/a`）

## 容错规则

- 字段缺失、空值、`null`：统一显示 `n/a`。
- JSON 为空、缺失或解析失败：显示 `invalid`（解析状态字段）或 `n/a`（业务字段）。
- live-readonly / live-control / mock 下字段不一致时，界面仍可打开。

## 新鲜度表达

- attention 与 gyro 刷新频率不同。
- attention 长时间未刷新不等于整条流断开，应通过 `attention_age_ms` / `attention_fresh` 观察。
- gyro 高频更新通过 `gyro_age_ms` / `gyro_fresh` 观察。

## warning_flags / error_flags（第一版语义）

- `warning_flags`: 非致命告警，提示链路或数据质量需要关注。
- `error_flags`: 影响可用性的错误标记，需定位问题来源。

## 非目标（TASK21 明确不包含）

- 页面切换框架
- GameCanvas 恢复或小游戏画布渲染
- 素材系统接入
- 训练管线重构
