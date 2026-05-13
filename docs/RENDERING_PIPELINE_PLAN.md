# RENDERING_PIPELINE_PLAN

1. Task8A/8B 只实现 Headless Game Core 与 Renderer Contract。
2. 当前没有真实 renderer 实现。
3. 未来 Pygame Renderer 只消费 GameViewState。
4. 未来 Web Dashboard 只消费 GameViewState / RuntimeSnapshotView。
5. Renderer 输入必须转换为 RuntimeCommand 或 GameEvent.user_action。
6. Renderer 不能访问数据库、设备、校准、SessionManager。
7. 渲染层不计算 FI。
8. 渲染层不结束 session。
9. 渲染层不直接写训练摘要。
10. Pygame/Web/平台嵌入是 renderer adapter，不改变 Runtime Contract。
11. GameViewState 是游戏层到渲染层的唯一稳定出口。

12. Task8C 增加双向 live pipeline runner，但仍不实现真实 renderer。
