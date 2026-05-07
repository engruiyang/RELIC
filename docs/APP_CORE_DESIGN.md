# RELIC Headless App Core 设计说明

- 分层：Data Bridge -> App Core -> UI Adapter/Games/Reports。
- 边界：Data Bridge 负责 IPC 收发解析，App Core 只读 snapshot。
- 本阶段不做正式 GUI：先保证内核稳定、可测试、可复用。
- RealtimeSnapshot：统一 attention/focus/gyro/设备状态字段。
- 频率差异：attention 低频，保留最近值并输出 age；gyro/focus 高频实时覆盖。
- 输入系统：InputEvent + InputManager 队列，CLI/后续 PyQt 都可接入。
- 游戏插件：BaseGame + GameContext，游戏不直接碰 socket/IPC。
- 资源协议：AssetManager 管理 manifest/theme，逻辑层不硬编码美术路径。
- Session：JSONL 事件 + summary JSON，统一日志出口。
- cleanup：重复调用安全，按 game -> session -> bridge 释放。
- 后续 PyQt 接入：在 UI Adapter 将 Qt 事件转换为 InputEvent，并调用 AppCore.tick/handle_input。
