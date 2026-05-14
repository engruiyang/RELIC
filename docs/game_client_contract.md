# GameClient 接入契约（TASK 16）

## 1. GameClientPort 方法

小游戏应实现以下方法（见 `game/game_contracts.py`）：

- `game_id`：稳定标识。
- `manifest`：能力声明和动作映射。
- `start(context)`：初始化状态。
- `stop(reason)`：收尾与完成标记。
- `update(runtime_snapshot, dt_ms)`：逐帧更新状态机。
- `handle_input(game_input_event)`：输入处理与命中判定。
- `build_game_view()`：输出 `GameViewState`。
- `collect_game_events()`：输出并清空 `GameEvent` 队列。
- `collect_behavior_sample()`：输出行为统计样本。
- `is_completed()`：告知主控是否完成。
- `get_score()`：返回当前分数。

## 2. GameInputEvent 字段

- `event_id` / `session_id` / `game_id`
- `input_type`（例如 `pointer_click`）
- `created_at_ms`
- `source`
- `x_norm` / `y_norm`（0~1 逻辑坐标）
- `button`
- `raw_event_type`
- `debug_hit`（可选）
- `payload`（扩展字段）

## 3. GameViewState 字段

- `game_id`
- `view_version`（当前 `game_view.v1`）
- `frame_id`
- `score` / `combo` / `level`
- `hud`
- `entities: list[GameEntity]`
- `visual_events: list[VisualEvent]`
- `layout_hints`

## 4. GameEntity 字段

- `id` / `kind` / `role`
- `x` / `y` / `radius`
- `state`
- `style_key` / `asset_key`
- `interactive`
- `hit_shape`
- `metadata`

## 5. VisualEvent 字段

- `event_id`
- `kind`
- `target_id`
- `x` / `y`
- `effect_key`
- `style_key`
- `intensity`
- `duration_ms`
- `payload`

## 6. GameEvent 字段

- `schema_version`（如 `game_event.v1`）
- `event_id` / `session_id` / `game_id`
- `event_type`（如 `target_click` / `background_click`）
- `created_at_ms`
- `reportable`
- `payload`

## 7. BehaviorSample 字段

- `window_ms`
- `target_count` / `correct_count` / `omission_count`
- `false_action_count` / `action_count`
- `rt_samples_ms`
- `accuracy` / `omission` / `false_action` / `rt_stability`
- `game_specific`

## 8. mouse_action_map

`mouse_action_map` 是鼠标按钮到语义动作的映射，例如：

- `0 -> target_primary`
- `1 -> background`
- `2 -> send_test_click`

该映射用于动作语义，不代表平台协议或渲染细节。

## 9. asset_key / style_key / effect_key

- 三者都是语义键。
- 不允许写真实素材路径。
- 由后续素材系统/主题系统/渲染层解析。

## 10. 队友开发流程

1. 复制 `game/templates/minimal_game/minimal_game_client.py`。
2. 修改 `game_id`、manifest 与状态字段。
3. 实现输入判定与事件类型。
4. 实现 `build_game_view()` 输出实体和特效事件。
5. 实现 `collect_behavior_sample()` 输出行为统计。
6. 补充对应测试并通过回归。

## 11. 禁止事项

1. 不直接 `import PySide6`。
2. 不直接写 QML。
3. 不直接访问 SQLite。
4. 不直接访问 DataCenter。
5. 不直接调用 PlatformReporter。
6. 不生成 `ipc_mouse_data`。
7. 不计算最终 FI/SQI。
8. 不自己创建或结束 TrainingSession。
9. 不写真实素材文件路径。
10. 不把美术资源路径硬编码到游戏逻辑中。

## 12. 最小模板运行方式

- `pytest -q tests/test_minimal_game_template.py`

## 13. 测试方式

- 模板测试：`pytest -q tests/test_minimal_game_template.py`
- 契约测试：`pytest -q tests/test_game_contracts.py tests/test_fake_click_game_client.py`
- 渲染契约测试：`pytest -q tests/test_game_view_render_contract.py`
