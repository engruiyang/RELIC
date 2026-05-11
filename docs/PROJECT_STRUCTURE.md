# PROJECT_STRUCTURE

## 正式主线目录（当前）

- `core/`：Headless Control Core（应用装配、状态机、时钟、上下文）。
- `data/`：`RealtimeSnapshot` / `DataCenter` 与数据有效性聚合。
- `device/`：设备入口与 adapters（mock 等）。
- `platform/`：平台 IPC / live 输入边界与消息转换。
- `user/`：用户与 Profile 业务管理。
- `storage/`：本地存储（SQLite 等底层持久化）。
- `ui_cli/`：命令行 debug / smoke test 入口。
- `config/`：配置。
- `calibration/`：Task5 校准模块写入位置。
- `session/`：Task7 训练会话模块写入位置。
- `runtime/`：Task8 Runtime API 写入位置。
- `game/`：Task8 游戏管理模块写入位置。
- `assets/`：资源目录。
- `third_party/hnnk_demo/`：官方 demo 参考（非业务主线）。
- `docs/`：项目文档。

## 历史路径与兼容保留

- `relic_core/`：**历史路径（兼容保留）**。目前仍被历史测试与部分 live 适配调用引用，短期不删除；新增功能禁止写入。
- `games/`：**历史原型路径（兼容保留）**。正式游戏目录为 `game/`；新增功能禁止写入 `games/`。
- `profiles/`：历史 phase-1 路径（兼容保留），不属于正式用户系统；新用户相关功能统一写入 `user/ + storage/`。
- `relic_data_bridge.py`：**兼容保留**。目前仍被 `relic_core.bridge_adapter` 的 live 兼容加载路径使用；新增业务逻辑不得写入。

## 重复职责审计结论

1. `core/` vs `relic_core/`
   - `core/` 为正式控制主线。
   - `relic_core/` 仍有历史测试与桥接兼容依赖，先标记废弃并冻结。
2. `game/` vs `games/`
   - `game/` 为正式目录。
   - `games/` 仅保留历史原型兼容，不新增。
3. `user/` vs `profiles/`
   - 正式用户系统为 `user/ + storage/`。
   - `profiles/` 为历史 phase-1 目录，不再承载新功能。
4. `platform/`、`device/`、`data/` 与 `relic_data_bridge.py`
   - 正式运行链路在 `platform/`、`device/`、`data/`。
   - `relic_data_bridge.py` 暂为 live 兼容桥接保留。

## 后续任务写入位置

- Task5 校准：`calibration/`
- Task6 状态估计：优先 `data/` 下独立模块；如需新建 `estimation/`，需在本文件补充理由与边界。
- Task7 训练会话：`session/`
- Task8 Runtime API：`runtime/`
- Task8 游戏管理：`game/`
- Task9 平台报告：`platform/`

## 写入禁令

新功能不得写入以下历史路径：

- `relic_core/`
- `games/`
- `profiles/`（历史 phase-1，已废弃）
- `relic_data_bridge.py`（仅兼容保留）

## 命令文档同步规则

- 后续任何任务如果新增、修改或废弃 CLI/debug/test 命令，必须同步更新 `docs/COMMANDS.md`。
