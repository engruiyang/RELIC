# TraceLock Protocol Demo（痕迹锁定协议）

TraceLock Protocol 是痕迹锁定协议的首个可玩 GameClient demo。

- 它不是正式美术版本。
- 它只实现游戏逻辑。
- 它不接 QML。
- 它不接 PlatformReporter。
- 它不读取 assets/*.json。
- 它不读取真实素材文件。
- 它通过 asset_key/style_key/effect_key 与渲染层通信。

## RuntimeSnapshot 对 HUD/Hint 的影响
- `error_flags` 非空：`signal_error`
- `gyro_fresh=false`：`gyro_link_unstable`
- `attention_fresh=false`：`focus_sync_pending`
- `control_state=FATIGUED`：`rest_suggested`
- `control_state=DISTRACTED`：`refocus`
- `control_state=HIGH_FOCUS`：`trace_predict_stable`
- 其他：`locking`

## pointer_click 触发事件
- 命中 target：`target_click`（reportable=True）
- 未命中背景：`background_click`（reportable=True）
- 目标超时：`target_omitted`（reportable=False）

## GameViewState 实体
- `target`
- `focus_zone`
- `progress_ring`
- `timer_bar`

## BehaviorSample 指标
- `target_count` / `correct_count` / `omission_count` / `false_action_count` / `action_count`
- `accuracy` / `omission` / `false_action` / `rt_stability`
- game_specific: `combo` / `max_combo` / `level` / `level_change_count` / `mean_reaction_time_ms` / `rtv`
- game_specific: `attention_stale_frames` / `gyro_unstable_frames` / `stable_focus_frames` / `trace_drop_count` / `trace_seal_count`

## 后续接入 live-control
后续只需在上游将 RuntimeSnapshot 持续传入 `update(runtime_snapshot, dt_ms)`；该 demo 保持纯 GameClient 逻辑，不直接接入 live-control 或 GUI 组件。
