# TASK23B GUI 主流程验收与测试清单

## 1) TASK23B 范围

TASK23B 仅覆盖 GUI 主流程收束，不新增业务功能：

- User/Profile 页面主动作与反馈可见、可调用。
- Calibration 页面状态、列表、详情、启动与绑定路径可用。
- Training 页面 readiness 阻拦/放行、session 起停与状态反馈可用。
- Report 页面刷新、会话列表、会话详情与缺参反馈可用。

## 2) 已完成页面

### User / Profile

- List Users
- Switch User
- Load Selected User
- Show Profile Detail
- Profile Detail Popup
- Create / Load 空输入 `missing_input` 可见

### Calibration

- Status
- List Calibrations
- 下拉选择 `calibration_id`
- Show Selected Calibration
- Bind Selected Calibration
- Start IPC Calibration（含进度提示）
- 完整 phase prompts 可见
- Calibration Detail 可滚动查看

### Training

- Training Readiness
- 无用户 / 无有效 calibration 阻拦训练
- 有用户 + 有效 calibration 允许 Start Session
- session 计时正常
- Stop Session 正常
- 可产生反馈文件 / `report_path`

### Report

- Refresh Report
- List Sessions
- 下拉选择 `session_id`
- Show Selected Session
- `missing_session_id` 可见
- `report.export` 明确 deferred（不静默失败）

## 3) 主流程验收路径

1. 启动 GUI live-control。
2. 进入 User 页面，选择并加载用户。
3. 进入 Calibration 页面，查看状态与历史，启动校准并绑定目标校准。
4. 进入 Training 页面，刷新 readiness，确认阻拦/放行逻辑后 Start Session。
5. 在 Training 页面 Stop Session。
6. 进入 Report 页面，刷新报告、列出会话、查看目标 session 详情。

## 4) 明确非目标（本轮不做）

- GameCanvas 恢复属于 TASK24。
- 美工整理属于后续 UI polish。
- Report export 当前为 deferred。
- TASK6B 调参 GUI 不属于 TASK23B。

## 5) 实机测试命令

```powershell
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
python -m ui_cli.run_gui_minimal --mode live-control --host 127.0.0.1 --port 8000 --user-id TEST --db-path data/relic_local.db
```

## 6) pytest 回归测试命令

```bash
python -m py_compile gui/gui_facade.py
python -m py_compile gui/gui_bridge.py

python -m pytest tests/test_gui_user_page_visible_structure.py -vv
python -m pytest tests/test_gui_calibration_page_visible_structure.py -vv
python -m pytest tests/test_gui_training_page_visible_structure.py -vv
python -m pytest tests/test_gui_report_page_visible_structure.py -vv
python -m pytest tests/test_gui_task23b_main_flow_contract.py -vv

python -m pytest tests/test_gui_qml_loads.py -vv
python -m pytest tests/test_gui_qml_style_safety.py -vv
python -m pytest tests -k "gui" -vv
python -m pytest tests -vv
```

## 7) 当前已知限制

- `report.export` 当前仍为 deferred 状态，仅提供显式反馈。
- GameCanvas 暂未恢复，Training 页面以主流程控制与状态反馈为主。
- 当前 contract 测试偏静态约束（token/action/banned-pattern），不替代完整端到端业务仿真。
