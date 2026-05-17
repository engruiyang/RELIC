# TASK23 AppShell Commands

```powershell
python -m pytest tests/test_gui_app_shell.py tests/test_gui_art_asset_contract.py tests/test_gui_page_switching.py
python -m pytest tests/test_gui_qml_loads.py tests/test_gui_page_shell.py tests/test_gui_live_bus_status.py tests/test_gui_runtime_refresh.py tests/test_gui_action_contract.py tests/test_gui_minimal_controls.py tests/test_gui_feedback_state.py tests/test_gui_app_shell.py tests/test_gui_art_asset_contract.py tests/test_gui_page_switching.py
python -m pytest tests -k "gui"
python -m pytest tests/test_gui_render_resources.py tests/test_resource_managers.py
python -m ui_cli.run_gui_minimal --mode core-control --user-id TEST --db-path data/relic_local.db --duration-sec 120
python -m ui_cli.run_gui_minimal --mode live-readonly --host 127.0.0.1 --port 8000 --user-id TEST --db-path data/relic_local.db
python -m ui_cli.run_gui_minimal --mode live-control --host 127.0.0.1 --port 8000 --user-id TEST --db-path data/relic_local.db
```
