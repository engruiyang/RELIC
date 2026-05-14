from gui.gui_core_source import GuiCoreSnapshotSource


def test_core_source_snapshot_shapes(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "relic.db"))
    app_state = source.get_app_state()
    runtime = source.get_runtime_snapshot()
    session = source.get_session_state()
    assert app_state["source"] == "core_readonly"
    assert "source" in runtime
    assert session["source"] == "core_readonly"


def test_core_source_command_and_event_results(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "relic.db"))
    assert source.handle_command("refresh_snapshot", {})["status"] == "accepted"
    assert source.handle_command("start_mock_session", {})["reason"] == "readonly_rejected"
    assert source.handle_event("target_click", {})["reason"] == "readonly_ignored"
