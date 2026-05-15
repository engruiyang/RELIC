from __future__ import annotations

from pathlib import Path

from gui.gui_facade import GuiFacade


def test_minimal_gui_has_required_sections_and_controls() -> None:
    qml = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    for token in [
        "Protocol Select",
        "TraceLock Training",
        "Debug Panel",
        "Link Diagnostics",
        "Start Training Session",
        "Start Mock Session (Debug)",
        "Force L1",
        "Force L2",
        "Force L3",
        "Force L4",
        "Force L5",
        "Auto DDA",
    ]:
        assert token in qml
    for banned in ["PlatformReporter", "ipc_mouse_data", "SQLite", "assets/"]:
        assert banned not in qml


def test_live_control_training_report_path_exposed_and_fake_game_ok() -> None:
    f = GuiFacade(mode="live-control", game_id="trace_lock")
    f.handle_gui_command("start_training_session", {})
    assert f.last_command_result["status"] == "training_started"
    f.handle_gui_command("end_training_session", {})
    assert f.last_command_result["status"] in {"training_completed", "training_stopped"}
    ss = f.get_session_state()
    assert "report_path" in ss
    hud = f.get_game_hud()
    for k in ["score", "combo", "level"]:
        assert k in hud
    f.close()

    f2 = GuiFacade(mode="live-control", game_id="fake_game")
    f2.handle_gui_command("start_mock_session", {})
    assert f2.last_command_result["status"] == "live_debug_started"
    f2.close()

