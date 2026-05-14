from gui.gui_core_source import GuiCoreSnapshotSource


def test_core_control_dispatcher_basic_flow(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "relic.db"), source_mode="core_control", duration_sec=1)
    assert source.handle_command("load_demo_user", {})["status"] == "accepted"
    assert source.handle_command("refresh_snapshot", {})["status"] == "accepted"
    result = source.handle_command("start_mock_session", {"duration_sec": 1})
    assert result["status"] == "completed"
    assert result["accepted"] is True
    assert result["payload"].get("session_id") or result["payload"].get("log_path")
    report = source.handle_command("open_last_report", {})
    assert report["status"] in {"accepted", "failed"}
    assert source.handle_command("end_session", {})["status"] == "noop"
