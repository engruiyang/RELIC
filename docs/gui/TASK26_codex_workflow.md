# TASK26 Codex Workflow（TASK26A）

## 1. Codex 可以做什么
- 写文档。
- 生成 example JSON。
- 批量整理配置。
- 批量替换文案。
- 根据测试错误补字段。
- 跑测试并汇报。

## 2. Codex 不允许做什么
- 自由重构 QML。
- 修改 `MinimalGui.qml`。
- 修改 `TrainingPage.qml`。
- 删除 legacy GUI。
- 修改 `command_registry.py`。
- 发明 action_id。
- 绕过测试。
- 修改 bridge-only 架构。
- 大范围调整 guiBridge property。
- 引入 `Loader / Repeater / Timer / subprocess`。

## 3. 配置修改流程
1) 先确认 schema。
2) 再修改 example JSON。
3) 再运行测试。
4) 再根据测试错误做最小修复。
5) 不允许因为测试失败而删除测试。

## 4. 每次配置修改后建议运行的测试
- `pytest -q tests/test_task25e_asset_handoff_contract.py tests/test_design_pack_contract.py`
- `pytest -q tests/test_gui_task25_design_pack_consumption.py tests/test_gui_task25_game_canvas_asset_pack.py`
- `pytest -q tests/test_gui_qml_style_safety.py`
- `pytest -q tests/test_gui_real_pages.py tests/test_gui_page_action_panels.py tests/test_gui_page_actions_runtime.py`

## 5. 输出格式
每次 Codex 完成后必须给出：
- 修改文件列表。
- 是否改动现有运行文件。
- 是否新增核心 QML。
- 是否修改 action_id。
- 测试命令。
- 测试结果。
- 未确认的真实字段或 action_id。
- 下一步建议。
