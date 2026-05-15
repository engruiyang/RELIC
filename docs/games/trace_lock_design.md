# TraceLock Protocol / 痕迹锁定协议

## 1. 游戏定位
TraceLock Protocol 是 RELIC Core 的高频真目标锁定训练协议，用于训练快速反应、持续专注、反应时稳定性、误触控制与连续执行能力。

供应方启动文案：
- Qilin Logic Trace Predict loaded.
- Predict the trace. Close the lock.
- Qilin Logic Trace Predict 已载入。
- 预测痕迹，闭合锁定。

## 2. 世界观边界
- RELIC Core = Resonant Link Interface Core。
- 运行环境可称为 LinkOS 2.1。
- 用户身份可称为 Linker / 接入者。
- 硬件可称为 NAC-2 Syncwell。
- attention 数据可称为 Focus Sync。
- gyro 数据可称为 Gyro Link。
- 项目对外只能表述为“原创近未来赛博朋克风格认知训练系统”。
- 不得使用任何现成商业游戏的专有公司、角色、地名、UI、Logo、音乐或装备名。

## 3. 核心循环
1. spawn trace
2. active
3. pointer_click
4. trace_seal / lock_failed / trace_drop
5. feedback
6. next trace

## 4. 状态机
- idle
- ready
- running
- feedback
- signal_warning
- completed
- stopped

## 5. target 类型
- marked_trace
- burst_trace
- unstable_trace

## 6. GameViewState entities
- target
- focus_zone
- progress_ring
- timer_bar

## 7. entity 字段契约
- kind
- role
- state
- x
- y
- radius
- asset_key
- style_key
- interactive
- metadata

## 8. 协议事件类型（保持兼容）
- target_click
- background_click
- target_omitted
- score_update
- level_changed
- game_completed

说明：UI 文案可称 trace_seal / trace_drop，但协议事件名保持 target_click / target_omitted，兼容既有 PlatformReporter mock。

## 9. Platform mock 上报约定
- target_click: reportable=true, payload.target_index=0, payload.action_name=target_primary
- background_click: reportable=true, payload.target_index=1, payload.action_name=background
- target_omitted / score_update / level_changed / game_completed: reportable=false

## 10. BehaviorSample 指标
通用：
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

game_specific：
- combo
- max_combo
- level
- level_change_count
- mean_reaction_time_ms
- rtv
- attention_stale_frames
- gyro_unstable_frames
- stable_focus_frames
- trace_drop_count
- trace_seal_count

## 11. RuntimeSnapshot 使用边界
TraceLockClient 可以读取：
- attention
- attention_fresh
- gyro_fresh
- stream_alive
- control_state
- warning_flags
- error_flags

规则：
- attention_fresh=false -> hud hint focus_sync_pending 或 attention_stale
- gyro_fresh=false -> hud hint gyro_link_unstable 或 motion_unstable
- control_state=HIGH_FOCUS -> hud hint trace_predict_stable
- control_state=DISTRACTED -> hud hint refocus
- control_state=FATIGUED -> hud hint rest_suggested

边界：不得计算最终 FI/SQI；不得修改 DataCenter；不得直接访问设备流。

## 12. 动态难度
- level: 1-5
- 参数：target_radius、target_lifetime_ms、movement_enabled、movement_speed、burst_target_ratio
- 原则：表现稳定时升难度；误触/遗漏/反应波动变差时降难度；10 秒内最多变化 1 档。

## 13. 美工替换规则
- 小游戏只输出 asset_key / style_key / effect_key。
- 真实图片、动效、颜色由 assets/games/trace_lock/visual_manifest.json 和 theme.json 管理。
- 更换素材不得修改 TraceLockClient。
- 美术方向是原创近未来赛博朋克认知训练 UI，可使用霓虹、扫描线、暗底、数据痕迹、网络流、锁定框等通用视觉语言，不得使用现成商业游戏的具体 UI 或素材。

## 14. 禁止事项
- 不读取图片路径。
- 不读取 assets/*.json。
- 不调用 AssetManager。
- 不调用 ThemeManager。
- 不调用 LayoutManager。
- 不调用 QML。
- 不调用 PySide6。
- 不调用 PlatformReporter。
- 不生成 ipc_mouse_data。
- 不访问 SQLite。
- 不访问 DataCenter。
- 不访问 SessionManager。
- 不计算最终 FI/SQI。
- 不创建正式训练报告。

附加约束：小游戏不得直接读取素材文件（由资源管理层统一读取并下发）。
