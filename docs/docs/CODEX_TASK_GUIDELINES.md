# CODEX_TASK_GUIDELINES

## 通用约束（Task8 及后续）
1. 不要把业务逻辑堆在 `main.py`。
2. 不要把所有逻辑堆进 `AppController`。
3. 每个模块职责清晰。
4. 模块之间通过接口或消息传递数据。
5. 小游戏不能直接访问 `DeviceAdapter`。
6. 小游戏不能直接访问 `DataCenter` 内部变量。
7. 小游戏不能直接访问 SQLite。
8. 小游戏不能直接创建或结束 `TrainingSession`。
9. 小游戏不能修改 `StateMachine`。
10. 小游戏不能读取 `CalibrationManager`。
11. 平台 IPC 协议只能出现在 `platform/` 相关模块。
12. 真实设备协议只能出现在 `device/` 相关模块。
13. JSONL 高频日志与 SQLite 摘要存储分离。
14. Runtime API 消息必须 JSON serializable。
15. 当前任务之外的功能只保留接口，不擅自扩展实现。
16. 修改已有文档时优先追加或新建附录，不允许无理由重写。
17. 完成每轮任务后必须说明修改文件、运行命令、测试结果、当前限制。
