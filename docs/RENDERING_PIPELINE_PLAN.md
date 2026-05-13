# RENDERING_PIPELINE_PLAN

1. Task8A 只实现 Headless Game Core，不实现 Renderer。
2. `GameViewState` 是游戏逻辑输出给未来渲染层的中立数据模型。
3. 未来 Pygame Renderer 只消费 `GameViewState`，不直接读取 `FakeGameClient` 内部变量。
4. 未来 Web Dashboard 只消费 `GameViewState` 或 `RuntimeSnapshotView`。
5. Renderer 不允许直接访问 DeviceAdapter、DataCenter、SQLite、CalibrationManager、SessionManager。
6. Renderer 用户输入应转成 `RuntimeCommand` 或 `user_action` `GameEvent`。
7. 渲染层不计算 FI。
8. 渲染层不修改 session。
9. 渲染层不直接写训练摘要。
10. 渲染层可显示 score/combo/FI/SQI/control_state/feedback_hint。
11. 若后续使用 WebSocket，消息仍需 JSON serializable。
12. Pygame/Web/平台嵌入只是 renderer adapter，不改变 GameManager 与 Runtime Contract。
