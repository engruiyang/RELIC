# GAME_COMMUNICATION_PROTOCOL

## 1. 协议目标
- 主程序与小游戏解耦。
- 游戏只通过 Runtime API 收发消息。
- 小游戏禁止直接访问设备、DataCenter 内部对象、SQLite、CalibrationManager、SessionManager、StateMachine。

## 2. 核心消息类型
- RuntimeSnapshotView
- RuntimeCommand
- GameEvent

## 3. RuntimeSnapshotView 字段表
| 字段 | 说明 |
|---|---|
| schema_version | 协议版本，当前默认 `1.0` |
| session_id | 当前训练会话 ID |
| now_ms | 采样时间戳（ms） |
| user_id / game_id | 用户与游戏标识 |
| attention / attention_age_ms / attention_fresh | 注意力值及新鲜度 |
| gyro_x / gyro_y / gyro_z / gyro_age_ms / gyro_fresh | 陀螺仪值及新鲜度 |
| sqi / quality_state | 信号质量指标与状态 |
| fi_raw / fi_smoothed / fi_valid / fi_confidence | Focus Index 相关字段 |
| control_state / control_state_reason | 控制状态及原因 |
| warning_flags / error_flags | 警告与错误标记 |
| behavior_ready | 是否允许行为采样 |
| interval_ms / delta_ms | 采样间隔字段 |

## 4. RuntimeCommand 字段表
| 字段 | 说明 |
|---|---|
| schema_version | 协议版本，当前默认 `1.0` |
| command_id | 命令 ID |
| session_id / game_id | 会话与游戏标识 |
| command_type | 命令类型 |
| issued_at_ms | 命令发出时间（ms） |
| payload | 扩展参数（必须 JSON 可序列化） |

允许 `command_type`：
- `start_game`
- `pause_game`
- `resume_game`
- `stop_game`
- `set_difficulty`
- `set_feedback_mode`

## 5. GameEvent 字段表
| 字段 | 说明 |
|---|---|
| schema_version | 协议版本，当前默认 `1.0` |
| event_id | 事件 ID |
| session_id / game_id | 必填，会话与游戏标识 |
| event_type | 事件类型 |
| created_at_ms | 事件时间戳（ms） |
| payload | 事件载荷（必须 JSON 可序列化） |

允许 `event_type`：
- `score_update`
- `behavior_sample`
- `difficulty_request`
- `game_completed`
- `game_error`
- `user_action`

## 6. payload 约定
### behavior_sample
- 推荐字段：`window_ms`, `target_count`, `correct_count`, `omission_count`, `false_action_count`, `action_count`, `rt_samples_ms`, `accuracy`, `omission`, `false_action`, `rt_stability`
- 其中 `accuracy/omission/false_action/rt_stability` 会按契约归一到 `[0,1]`。

### score_update
- 推荐字段：`score`, `score_delta`, `combo`, `level`

### difficulty_request
- 推荐字段：`requested_level`, `reason`, `confidence`

### game_completed
- 推荐字段：`reason`, `final_score`, `user_finished`

### game_error
- 推荐字段：`code`, `message`, `recoverable`

### user_action
- 推荐字段：`action_type`, `target_id`, `success`, `rt_ms`

## 7. 游戏权限边界
1. 小游戏只能发 `difficulty_request`，不能直接变更难度。
2. 小游戏只能上报 `game_completed`，不能直接结束 TrainingSession。
3. 小游戏不能直接访问数据库、设备、校准模块或状态机。
4. Runtime API 是主程序与游戏之间唯一通信边界。

## 8. Task7 记录规则
- SessionManager 只记录标准 `GameEvent`，不依赖具体游戏类。
- `difficulty_request` 在 Task7 只做日志记录，不做决策。
- `game_completed` 是否导致会话结束由主程序协调层决定。
- 高频事件写入 `logs/sessions/*.jsonl`，摘要写入 SQLite `training_sessions`。

## 9. Task8 与后续实现约束
- Task8 FakeGame 必须遵守本协议。
- 后续 WebSocket/Pygame 接入也必须遵守本协议。
- 禁止以“临时直连对象”绕过 Runtime API。

## 10. 版本策略
- 当前 schema_version 按代码契约为 `1.0`。
- 破坏性变更必须显式升级版本并提供迁移说明。

## 11. Task8A FakeGameClient 使用方式
- FakeGameClient 仅通过 Runtime API 接收 `RuntimeSnapshotView` 与 `RuntimeCommand`。
- FakeGameClient 输出标准 `GameEvent`（`score_update` / `behavior_sample` / `difficulty_request` / `game_completed` / `game_error`）。
- `difficulty_request` 仅作为请求记录，不直接改用户 difficulty。
- `game_completed` 仅作为事件，不直接结束 session。
- `behavior_sample` 在 Task8A 只进入 SessionManager 记录链路，暂不接入 FocusEstimator。
