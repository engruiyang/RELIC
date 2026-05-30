# ShardLock Protocol（碎片锁定协议）设计文档

## 1) 游戏名称
- English: **ShardLock Protocol**
- 中文名：**碎片锁定协议**

## 2) 游戏定位
ShardLock Protocol 是一个**高频真目标锁定小游戏**，用于训练：
- 快速反应
- 持续专注
- 反应时稳定性
- 误触控制

## 3) 核心循环
1. spawn target
2. active
3. pointer_click
4. lock_success / lock_failed / target_omitted
5. next target

## 4) 状态机
- idle
- ready
- running
- feedback
- signal_warning
- completed
- stopped

## 5) target 类型
- primary_shard
- burst_shard
- unstable_shard

## 6) GameViewState entities
- target
- focus_zone
- progress_ring
- timer_bar

## 7) entity 字段约定
每类 entity 至少包含如下字段：
- kind
- role
- state
- x / y / radius
- asset_key
- style_key
- interactive
- metadata

## 8) GameEvent 类型
- target_click
- background_click
- target_omitted
- score_update
- level_changed
- game_completed

## 9) Platform mock 上报约定
- target_click: `target_index=0`, `action_name=target_primary`, `reportable=true`
- background_click: `target_index=1`, `action_name=background`, `reportable=true`
- 其他事件：`reportable=false`

## 10) BehaviorSample 指标
- target_count
- correct_count
- omission_count
- false_action_count
- action_count
- rt_samples_ms
- accuracy
- omission
- false_action
- rt_stability
- game_specific.combo
- game_specific.max_combo
- game_specific.level
- game_specific.rtv
- game_specific.attention_stale_frames
- game_specific.gyro_unstable_frames

## 11) RuntimeSnapshot 使用方式
- `attention_fresh=false` -> HUD hint: `attention_stale`
- `gyro_fresh=false` -> HUD hint: `motion_unstable`
- `control_state` 的 `HIGH_FOCUS / DISTRACTED / FATIGUED` 只影响提示和难度边界，不计算 FI/SQI。

## 12) 动态难度
- level: 1-5
- 调节参数：
  - target_radius
  - target_lifetime_ms
  - movement_enabled
  - burst_target_ratio
- 约束：10 秒内最多变化 1 档。

## 13) 美工替换规则
- 小游戏只输出 key（asset_key/style_key/effect_key）。
- 真实图片、动效、颜色在：
  - `assets/games/shard_lock/visual_manifest.json`
  - `assets/themes/*/theme.json`
  中替换。
- 更换素材不改 ShardLockClient。

## 14) 禁止事项
- 不读取图片路径。
- 不读取 assets/*.json。
- 不调用 AssetManager / ThemeManager / LayoutManager。
- 不调用 QML / PySide6。
- 不调用 PlatformReporter。
- 不生成 ipc_mouse_data。
- 不访问 SQLite / DataCenter / SessionManager。
- 不计算最终 FI/SQI。

## 15) 资源契约与代码分层说明
- ShardLockClient 只生产行为与可视 key，不读取素材文件。
- Python 资源层负责读取 manifest/theme/layout 并做解析。
- QML 仅消费桥接后的只读 JSON，不直接读取 manifest 文件。
