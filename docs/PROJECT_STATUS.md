# PROJECT_STATUS

## 总览
- Task1~Task5：核心数据链路、用户管理、校准流程与基础 CLI 调试链路已完成并可回归验证。
- Task6B：实现闭环已完成，当前处于参数收敛与文档归档阶段。
- Task7A/Task7B：Session 记录与摘要统计功能已闭环，正在进行 Task8 前清理。
- Task8：尚未开始开发业务实现。

## Task1~Task5（简述）
- 已完成主程序骨架、DataCenter 基础链路、用户与校准管理、核心调试 CLI 与对应测试覆盖。

## Task6B（SQI / FI / control_state）
- 已完成：
  - QualityGate
  - FocusEstimator
  - ControlStateEstimator
  - runtime_snapshot 输出 SQI/FI/control_state 字段
  - 帧级标注 CSV 流程
  - `evaluate_task6b`
  - `tune_task6b`
- 未完成：live 数据人工复核后的参数最终选择。
- 状态：**implementation closed, parameter tuning pending**。
- 边界：后续只通过 config 调参，不随意改公式实现。

## Runtime Contract
- 已完成：
  - RuntimeSnapshotView
  - RuntimeCommand
  - GameEvent
  - LocalRuntime
  - GameManifest
- 状态：**contract frozen for Task8A**。
- 边界：
  - 消息必须 JSON serializable。
  - 小游戏只能通过 Runtime API 与主程序通信。

## Task7A
- 已完成：
  - SessionManager 最小闭环
  - `logs/sessions/` JSONL 会话日志
  - SQLite `training_sessions` 摘要落库

## Task7B
- 已完成：
  - duration summary
  - FI/SQI min/max/last
  - GameEvent 摘要统计
  - session 查询 CLI（list/show）
- 状态：**functionally closed, docs cleanup in progress**。

## Task8
- 状态：尚未开始。
- 进入条件：Pre-Task8 Cleanup 完成且回归测试与 CLI 验证通过。

## Task8A
- 状态：in progress（本轮实现 Headless GameManager + FakeGameClient 最小闭环）。
- 已完成：GameManager 注册/选择/启动/停止，FakeGameClient 事件发射，GameViewState 中立视图模型，run_game_debug CLI。
- 未完成：Pygame/Web 渲染适配器与正式动态难度策略。
