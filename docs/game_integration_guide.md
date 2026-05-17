# Game Integration Guide (TASK22)

## 1) TASK22 定位
TASK22 用于固化小游戏接入总线与队友参考链路；不恢复 GameCanvas，不做正式训练页，不做页面切换。

## 2) 总体链路
RuntimeSnapshotView -> GameClient.tick/update(snapshot) -> GameViewState -> GameEvent/BehaviorSample -> GameManager -> SessionManager / PlatformReporter mock / GUI HUD。

## 3) 现有参考实现
- **TraceLock / 碎片锁定**：完整玩法与事件链路参考（优先）。
- **minimal_game_template**：最小可复制结构参考。
- **fake_game / fake_click**：协议与测试链路参考。

TraceLock 适合学习完整循环；minimal template 适合新游戏起步；fake/fake_click 适合验证 Runtime API 和事件流。

## 4) 角色职责
- **RuntimeSnapshotView**：只读输入（attention/gyro/SQI/FI/control_state/warning_flags/error_flags/session_id/game_id）。
- **GameInputEvent**：输入事实（click/drag/key/hover/hold + 坐标 + 时间戳 + payload）。
- **GameClient**：核心逻辑；处理 snapshot/input；输出 GameViewState + GameEvent + BehaviorSample。
- **GameViewState**：渲染中立模型，不含 QML/PySide/Pygame 对象。
- **GameEvent**：标准事件（score_update/behavior_sample/difficulty_request/game_completed/game_error/user_action）。
- **BehaviorSample**：行为窗口摘要（action_count/accuracy/omission/false_action/rt_stability/rt_samples_ms）。
- **Renderer/QML**：只显示 GameViewState；只上报输入事实；不判断命中、不加分、不写 GameEvent。
- **GameManager**：注册/分发 snapshot/收集 GameEvent/校验 session_id/game_id/转交 SessionManager。
- **SessionManager**：记录训练过程，游戏不能直接调用。
- **PlatformReporter mock**：只消费标准 GameEvent。

## 5) 新小游戏 checklist
1. 复制 minimal template 或参考 TraceLock。
2. 定义 game_id。
3. 实现 start/reset。
4. 实现 update/tick(snapshot)。
5. 实现 handle_input(event)。
6. 输出 GameViewState。
7. 输出 score_update GameEvent。
8. 窗口化输出 behavior_sample GameEvent。
9. 不访问底层模块。
10. 补测试。
11. 用 run_game_debug 验证 mock。
12. 有 live 时再验证 live pipeline。

## 6) 输入事件规范
推荐字段：event_type, x/y(或 normalized_x/normalized_y), timestamp_ms, pointer_id(可选), payload。
强调：QML 只传输入事实；命中判断在游戏端；QML 不判断得分；QML 不直接写 GameEvent。

## 7) 输出事件规范
GameEvent 推荐字段：schema_version, event_id, session_id, game_id, event_type, created_at_ms, payload。
推荐 event_type：score_update, behavior_sample, difficulty_request, game_completed, game_error, user_action。

## 8) GameViewState 规范
至少包含：schema_version/view_version, session_id(如可用), game_id, view_type(如可用), updated_at_ms/frame_id, status, score, combo, level, control_state, quality_state, feedback_hint, hud, entities, effects/visual_events, layout_hints。

## 9) BehaviorSample 规范
推荐：window_ms, target_count, correct_count, omission_count, false_action_count, action_count, rt_samples_ms, accuracy, omission, false_action, rt_stability。
BehaviorSample 当前进入 SessionManager 记录链路；后续 Task6C/S_B 再与 FocusEstimator 更深耦合；游戏当前不得直接修改 FI。

## 10) 禁止事项
小游戏禁止直接访问：DeviceManager/DataCenter/SQLite/CalibrationManager/SessionManager/StateMachine；禁止直接结束 TrainingSession、改用户 profile、改难度 profile、直接上传平台报告；禁止依赖 QML 私有对象；禁止输出不可 JSON 序列化对象。

## 11) 与 TASK21 的关系
TASK21 的 Developer Diagnostics Console 只显示 Game HUD 摘要。TASK22 固化小游戏接入协议与参考链路。GameCanvas 恢复留 TASK24；页面切换留 TASK23。

## 12) 与 TASK6-TASK9 的关系
TASK6 的 SQI/FI/control_state 进入 RuntimeSnapshotView；TASK7 的 SessionManager 记录 GameEvent；TASK8 的 Runtime API/GameManager 负责双向管线；TASK9 的 PlatformReporter/ReplayAdapter 只消费标准事件。

## 13) 审查结论（本仓）
1. TraceLock 已有 GameClient：`game/examples/trace_lock/trace_lock_client.py`。
2. TraceLock 输出 GameViewState：`build_game_view()`。
3. TraceLock 输出 GameEvent：`collect_game_events()` + `_make_event(...)`。
4. 已有 BehaviorSample：`collect_behavior_sample()`。
5. 输入事件通过 `GameInputEvent` 进入 `handle_input(...)`。
6. QML/GUI 只传输入事实；命中判断在游戏端（见 fake_click/trace_lock 的 `_is_hit` 与 handle_input）。
7. GameClient 未导入 device/data/storage/calibration/session/platform 底层模块（见 trace_lock/minimal/fake_click）。
8. PlatformReporter mock 只消费标准 GameEvent（测试已覆盖）。
9. 最适合队友模板：`game/templates/minimal_game/minimal_game_client.py`；完整参考为 TraceLock。
10. 证明链路有效的测试：`test_game_contracts`, `test_minimal_game_template`, `test_fake_click_game_client`, `test_game_view_render_contract`, `test_game_event_to_platform_mock`, `test_task8_game_flow`, `test_task8_live_game_pipeline`, TraceLock 系列。
11. 当前主要短板是文档聚合不足（本任务已补），不是核心代码缺陷。
12. 命名上存在 TraceLock/ShardLock/碎片锁定并行称呼；当前规范名称沿用 `trace_lock`（不做大规模重命名）。


## 14) TASK22-FINALIZE 验收补充（append-only）
- `run_game_debug` 是**无头 CLI pipeline** 验收入口，不会打开 GUI 窗口。
- live 命令若报 `ConnectionRefusedError`，通常表示平台 `127.0.0.1:8000` 未启动或未就绪；请先启动平台后重试。
- TASK22 成功验收标准：
  - RuntimeSnapshotView 可见；
  - attention / gyro / sqi / fi / control_state 可见；
  - GameViewState 可见；
  - score_update_count 增长；
  - behavior_sample_count 在有效信号后增长；
  - GameEvent 符合协议；
  - TraceLock 相关测试通过。
- GUI 弹窗不是 TASK22 验收目标。
- GUI 页面切换属于 TASK23。
- GameCanvas 恢复属于 TASK24。
