# TASK 13/14 GUI Mouse Pipeline Commands (PowerShell)

> 说明：本文件仅补充 TASK 13 / TASK 14 相关运行、测试、人工验收与架构检查命令。所有命令均为 Windows PowerShell 可直接执行写法。

## 1) 运行 core-control GUI

**用途**：启动 Minimal GUI 的 core-control 模式，联调 GUI 命令、鼠标输入、GameClient、PlatformReporter mock 链路。

**命令**：

```powershell
python -m ui_cli.run_gui_minimal --mode core-control --db-path data/relic_local.db --duration-sec 3 --user-id demo_user --game-id fake_game --task6b-config config/task6b.yaml
```

**预期/验收重点**：
- 启动后看到 `[GUI] mode=core-control`。
- 点击 **Start Mock Session** 后看到 mock session completed。
- 点击目标后看到 `GAME EVENT target_click` 且 `PLATFORM MOCK ipc_mouse_data index=0`。
- 点击背景后看到 `GAME EVENT background_click` 且 `PLATFORM MOCK ipc_mouse_data index=1`。

---

## 2) TASK 14 全链路测试

**用途**：验证小游戏契约、FakeClickGameClient、GUI 鼠标到 GameClient、GameEvent 到 PlatformReporter mock。

**命令**：

```powershell
pytest -q tests/test_game_contracts.py tests/test_fake_click_game_client.py tests/test_gui_mouse_to_game_client.py tests/test_game_event_to_platform_mock.py
```

**当前已知通过结果**：
- `21 passed`

---

## 3) GUI 回归测试

**用途**：确认 GUI protocol/facade/bridge/core source/dispatcher/core-control/mouse input 行为未被破坏。

**命令**：

```powershell
pytest -q tests/test_gui_protocol.py tests/test_gui_facade.py tests/test_gui_bridge.py tests/test_gui_core_source.py tests/test_gui_command_dispatcher.py tests/test_gui_core_control.py tests/test_gui_mouse_input.py
```

**当前已知通过结果**：
- `18 passed`（不同环境可能出现 `skipped`）

---

## 4) TASK 9 报告 / Replay / PlatformReporter 回归

**用途**：确认平台报告兼容层、ReplayAdapter、Task9 e2e、SessionReportWriter 未被破坏。

**命令**：

```powershell
pytest -q tests/test_platform_reporter.py tests/test_replay_adapter.py tests/test_task9_e2e_demo.py tests/test_session_report_writer.py
```

**当前已知通过结果**：
- `5 passed`

---

## 5) Headless 主线回归

**用途**：确认 Runtime contract、SessionManager、GameManager、Task8 game flow 未被破坏。

**命令**：

```powershell
pytest -q tests/test_runtime_contract.py tests/test_session_manager.py tests/test_game_manager.py tests/test_task8_game_flow.py
```

**当前已知通过结果**：
- `29 passed`

---

## 6) TASK 13/14 总回归命令

**用途**：一次性跑 TASK 13 / 14 + GUI + TASK9 + headless 主线。

**命令**：

```powershell
pytest -q tests/test_game_contracts.py tests/test_fake_click_game_client.py tests/test_gui_mouse_to_game_client.py tests/test_game_event_to_platform_mock.py tests/test_gui_protocol.py tests/test_gui_facade.py tests/test_gui_bridge.py tests/test_gui_core_source.py tests/test_gui_command_dispatcher.py tests/test_gui_core_control.py tests/test_gui_mouse_input.py tests/test_platform_reporter.py tests/test_replay_adapter.py tests/test_task9_e2e_demo.py tests/test_session_report_writer.py tests/test_runtime_contract.py tests/test_session_manager.py tests/test_game_manager.py tests/test_task8_game_flow.py
```

**当前已知通过结果**：
- `71 passed`

---

## 7) QML 架构污染检查

**用途**：确认 QML 未直接接触平台协议、PlatformReporter、SessionManager、DeviceAdapter。

**命令**：

```powershell
Get-ChildItem -Path ui_qml -Recurse -Include *.qml | Select-String -Pattern "ipc_mouse_data|PlatformReporter|SessionManager|DeviceAdapter"
```

**预期**：
- 无输出。

---

## 8) game/gui/ui_qml 架构污染检查

**用途**：检查 game、gui、ui_qml 是否出现越界依赖。

**命令**：

```powershell
Get-ChildItem -Path game,gui,ui_qml -Recurse -Include *.py,*.qml | Select-String -Pattern "ipc_mouse_data|PlatformReporter|SessionManager|DeviceAdapter"
```

**预期说明**：
- `ui_qml` 不应命中。
- `gui_bridge.py` 不应命中 `PlatformReporter`。
- `FakeClickGameClient` 不应命中 `PlatformReporter`。
- 允许专用 adapter 命中 `PlatformReporter`。
- 允许既有 `game_pipeline.py` 命中 `SessionManager`（既有结构，非 TASK 13/14 新增越界）。

---

## 9) 查看最新训练报告

**用途**：查看最近生成的 Markdown 报告。

**命令**：

```powershell
Get-ChildItem reports/sessions -File | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, LastWriteTime, Length
```

---

## 10) 用 UTF-8 查看最新报告

**用途**：避免 PowerShell 默认编码导致中文乱码。

**命令**：

```powershell
$latest = Get-ChildItem reports/sessions -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $latest.FullName -Encoding UTF8 -TotalCount 60
```

**说明**：
- 查看中文报告建议显式加 `-Encoding UTF8`。

---

## 11) TASK 14 人工验收流程

**用途**：人工确认 core-control 下 GUI→GameClient→Platform mock 行为正确。

1. 运行 core-control GUI（见第 1 节命令）。
2. 点击 **Start Mock Session**。
3. 等待 PowerShell 输出 mock session completed。
4. 点击目标区域。
5. 应看到：
   - `[GAME EVENT] event_type=target_click target_index=0 action=target_primary`
   - `[PLATFORM MOCK] type=ipc_mouse_data index=0 action=target_primary`
6. 点击背景区域。
7. 应看到：
   - `[GAME EVENT] event_type=background_click target_index=1 action=background`
   - `[PLATFORM MOCK] type=ipc_mouse_data index=1 action=background`
8. GUI event result 应为：
   - `game_event_recorded_and_platform_mocked`
9. 不应连接真实平台 socket。
10. QML 不应报错。

---

## 12) 已知限制（当前阶段）

1. `start_mock_session` 当前为同步短流程，GUI 可能短暂卡顿约 1 秒。
2. `PlatformReporter` 当前使用 `InMemory/mock sender`。
3. 当前未接真实平台 socket。
4. 当前未做真实官方平台联调。
5. 当前 `Minimal GUI` 仍是工程探针，不是正式页面。
6. 当前 `GameViewState` 只回传摘要，尚未驱动正式通用 `GameCanvas` 渲染。
7. 当前尚未做正式素材系统、美术、主题和页面重布局。

## TASK 16 模板与接入文档命令（PowerShell）

- 运行模板测试：`pytest -q tests/test_minimal_game_template.py`
- 运行小游戏契约测试：`pytest -q tests/test_game_contracts.py tests/test_fake_click_game_client.py`
- 运行 TASK 15 渲染契约测试：`pytest -q tests/test_game_view_render_contract.py`
- 运行 TASK 14 全链路测试：`pytest -q tests/test_gui_mouse_to_game_client.py tests/test_game_event_to_platform_mock.py`
- 运行 GUI 回归：`pytest -q tests/test_gui_protocol.py tests/test_gui_facade.py tests/test_gui_bridge.py tests/test_gui_core_source.py tests/test_gui_command_dispatcher.py tests/test_gui_core_control.py tests/test_gui_mouse_input.py`
- 运行 TASK 9 回归：`pytest -q tests/test_platform_reporter.py tests/test_replay_adapter.py tests/test_task9_e2e_demo.py tests/test_session_report_writer.py`
- 运行 headless 回归：`pytest -q tests/test_runtime_contract.py tests/test_session_manager.py tests/test_game_manager.py tests/test_task8_game_flow.py`

## TASK 16A 头环实机 live stream headless 验收 CLI（PowerShell）

- 运行 fake/live-stream 单测：`pytest -q tests/test_live_stream_check.py`
- 运行实机验收：`python -m ui_cli.run_live_stream_check --host 127.0.0.1 --port 8000 --duration-sec 30 --db-path data/relic_local.db --output-dir logs/live_stream_checks`
