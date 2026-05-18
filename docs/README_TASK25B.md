TASK25B Design Pack Consumption Patch

Scope:
- MinimalGui parses guiBridge.renderResourcesJson into design pack objects.
- TrainingPage receives and displays design pack/page/component/game/effect token status.
- GameCanvas consumes trace_lock game_styles/effect_styles for canvas background, target fill/stroke/glow, progress ring, timer bar, and lightweight visual-event fallback.
- Tests updated to lock design-pack consumption without changing control logic.

Control logic intentionally untouched:
- No changes to gui_facade.py, gui_bridge.py, TraceLockClient, session/report/calibration, DataCenter, RealtimeSnapshot, MockAdapter.
- No Loader, subprocess, Popen, os.system.
- GameCanvas pointer_click path remains guiBridge.sendEvent("pointer_click", ...).

Files:
- ui_qml/MinimalGui.qml
- ui_qml/pages/TrainingPage.qml
- ui_qml/components/GameCanvas.qml
- tests/test_gui_task24_game_canvas_contract.py
- tests/test_gui_training_page_visible_structure.py
- tests/test_gui_render_resources.py
- tests/test_gui_task25_design_pack_consumption.py

Suggested tests:
python -m pytest tests/test_gui_task25_design_pack_consumption.py -vv
python -m pytest tests/test_gui_task24_game_canvas_contract.py -vv
python -m pytest tests/test_gui_training_page_visible_structure.py -vv
python -m pytest tests/test_gui_render_resources.py -vv
python -m pytest tests/test_gui_qml_loads.py -vv
python -m pytest tests/test_gui_qml_style_safety.py -vv
python -m pytest tests -k "gui" -vv
python -m pytest tests -vv
