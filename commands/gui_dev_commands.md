# RELIC GUI / Headless 常用开发命令（PowerShell）

> 适用范围：TASK 12（含 12A）到 TASK 13 开始前的日常开发/验收。  
> 约定：以下命令均为 **Windows PowerShell 可直接执行** 写法。  
> 注意：长命令如需换行，请使用 PowerShell 反引号 `` ` ``，不要使用 Unix 反斜杠续行。

## 模式说明（Minimal GUI）

- `--mode mock`：纯 mock 数据源，用于 GUI 基础交互验证。
- `--mode core`：core readonly，只读快照，不启动训练；`start_mock_session` 会被拒绝。
- `--mode core-control`：受控命令模式，可触发短 mock session，并回填 `report_path`。

> 项目状态备注：在 TASK 13 开始前，TASK 12 已完成 core-control 短 mock session 触发、`report_path` 回填、以及报告字段映射修复。

---

## 1) TASK 9 headless e2e 验收

用途：执行 TASK 9 端到端 mock 流程，生成日志与报告。

```powershell
python -m ui_cli.run_task9_e2e_demo --db-path data/relic_local.db --duration-sec 3 --user-id demo_user --game-id fake_game --task6b-config config/task6b.yaml
```

## 2) 查看最新训练报告

用途：按时间倒序查看最新 5 份报告。

```powershell
Get-ChildItem reports/sessions -File | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, LastWriteTime, Length
```

## 3) 用 UTF-8 查看最新报告（避免中文乱码）

用途：读取最新报告前 60 行；PowerShell 查看中文请显式 `-Encoding UTF8`。

```powershell
$latest = Get-ChildItem reports/sessions -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $latest.FullName -Encoding UTF8 -TotalCount 60
```

## 4) 运行 mock GUI

用途：验证 GUI 最小链路与 mock 命令交互。

```powershell
python -m ui_cli.run_gui_minimal --mode mock
```

## 5) 运行 core readonly GUI

用途：验证 core 只读模式（不启动训练）。

```powershell
python -m ui_cli.run_gui_minimal --mode core --db-path data/relic_local.db
```

## 6) 运行 core-control GUI

用途：验证受控命令模式，可触发短 mock session。

```powershell
python -m ui_cli.run_gui_minimal --mode core-control --db-path data/relic_local.db --duration-sec 3 --user-id demo_user --game-id fake_game --task6b-config config/task6b.yaml
```

## 7) GUI 测试

用途：验证 GUI 协议、Facade、Bridge、Core Source、Dispatcher、core-control 行为。

```powershell
pytest -q tests/test_gui_protocol.py tests/test_gui_facade.py tests/test_gui_bridge.py tests/test_gui_core_source.py tests/test_gui_command_dispatcher.py tests/test_gui_core_control.py
```

## 8) TASK 9 报告 / Replay / PlatformReporter 回归

用途：验证 TASK 9 报告链路与 replay/platform reporter 回归。

```powershell
pytest -q tests/test_platform_reporter.py tests/test_replay_adapter.py tests/test_task9_e2e_demo.py tests/test_session_report_writer.py
```

## 9) headless 回归

用途：验证核心 headless 流程的主回归集。

```powershell
pytest -q tests/test_runtime_contract.py tests/test_session_manager.py tests/test_game_manager.py tests/test_task8_game_flow.py
```

## 10) 检查 GUI 层是否越界调用平台 IPC 或核心内部模块

用途：静态扫描 GUI/QML 层敏感调用关键字。

```powershell
Get-ChildItem -Path gui,ui_qml -Recurse -Include *.py,*.qml | Select-String -Pattern "ipc_mouse_data|PlatformReporter|SessionManager|DataCenter|DeviceAdapter"
```

## 11) 查最新日志中的关键训练事件

用途：查看最新 session 日志中的关键事件（启动/结束/快照/游戏事件/summary）。

```powershell
$latestLog = Get-ChildItem logs/sessions -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Select-String -Path $latestLog.FullName -Pattern "session_start|session_end|runtime_snapshot|game_event|session_summary"
```
