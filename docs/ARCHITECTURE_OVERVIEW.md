# ARCHITECTURE_OVERVIEW

## 当前整体链路
PlatformGateway / DeviceAdapter  
↓  
DataCenter / RealtimeSnapshot  
↓  
QualityGate / FocusEstimator / ControlStateEstimator  
↓  
RuntimeSnapshotView  
↓  
Runtime API  
↓  
GameManager / GameClient  
↓  
GameEvent  
↓  
SessionManager  
↓  
JSONL + SQLite Summary

## 关键职责边界
1. **DataCenter 是实时数据来源**，提供 attention/gyro 等基础观测。
2. **Task6B 估计器负责 SQI/FI/control_state**，属于运行时估计层。
3. **Runtime API 是主程序与游戏之间唯一通信边界**。
4. **SessionManager 只记录，不重新计算 FI**。
5. **JSONL 保存高频事件，SQLite 保存摘要**。
6. **`logs/task6b/` 用于 Task6B 调参与标注数据**。
7. **`logs/sessions/` 用于正式训练 session**。
8. **小游戏不得直接访问设备、数据库、校准、SessionManager 或状态机**。

## Task8 前冻结说明
- Runtime 契约语义（RuntimeSnapshotView / RuntimeCommand / GameEvent）在 Task8A 前冻结。
- Task8 仅允许在 `game/` 与协调层做实现，不得反向侵入估计器、校准或存储职责。

## Task8A Headless Game 闭环
RuntimeSnapshotView -> LocalRuntime.publish_snapshot() -> FakeGameClient -> GameEvent -> GameManager -> SessionManager.record_game_event().

渲染预留链路：FakeGameClient -> GameViewState -> GameManager.get_current_view_state() -> Future Renderer。
