# RELIC 最小游戏模板（TASK 16）

该目录用于给队友复制一个可运行的 `GameClient` 起点。小游戏本质是**游戏状态机**，只接收输入与快照、只输出中立协议，不直接耦合 GUI/平台/数据库。

## 模板边界

- 小游戏不负责 QML 渲染。
- 小游戏不负责加载真实图片或音频文件。
- 小游戏不负责平台 `ipc_mouse_data`。
- 小游戏不写 SQLite。
- 小游戏不访问 DataCenter。
- 小游戏不直接调用 PlatformReporter。

## 输入与输出

输入：
- `GameInputEvent`（如 pointer_click）
- `RuntimeSnapshot`（在 `update(runtime_snapshot, dt_ms)` 中消费）

输出：
- `GameViewState`：告诉 GUI “画什么”。
- `GameEvent`：告诉主控“发生了什么”。
- `BehaviorSample`：给 FI/SQI 行为评价提供数据。

## 资源 key 规则

- `asset_key` / `style_key` / `effect_key` 只是语义 key。
- 它们**不是**真实文件路径。
- 不要在逻辑中写 `assets/...`、`.png`、`.wav` 等路径。
- 目标移动由小游戏输出逻辑坐标（0~1 归一化）。
- 爆炸、粒子、动画由 `VisualEvent` 表达，渲染器负责播放。

## 点击判定规则

- QML 点击命中仅作 debug 参考。
- 最终命中必须由 GameClient 根据自己的 hit rule 判定。

## report 规则

- `GameEvent.reportable=True` 的事件由上游决定是否送到 PlatformReporter。
- 小游戏只产出 `GameEvent`，不直接调用 PlatformReporter。

## manifest.example.json 说明

`manifest.example.json` 展示能力声明与动作映射。

> JSON 不支持注释，因此字段解释放在 README / docs。

核心字段：
- `game_id` / `display_name` / `version`
- `supported_inputs` / `supported_entities` / `supported_effects`
- `default_difficulty`
- `mouse_action_map`（示例：0->target_primary, 1->background, 2->send_test_click）
- `report_enabled`

## 如何复制开始新游戏

1. 复制 `minimal_game_client.py` 到你的新目录并改类名。
2. 修改 `game_id` 与 `manifest`。
3. 替换 `_is_target_hit()` 与 `handle_input()` 规则。
4. 在 `build_game_view()` 输出你的 `entities` 与 `visual_events`。
5. 在 `collect_behavior_sample()` 输出你的行为统计。
6. 运行 `pytest -q tests/test_minimal_game_template.py` 验证模板契约。
