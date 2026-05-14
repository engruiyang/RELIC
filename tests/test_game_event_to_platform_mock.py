from gui.game_event_platform_adapter import GameEventPlatformAdapter
from gui.gui_core_source import GuiCoreSnapshotSource


def test_not_reportable_event_skips_platform_mock() -> None:
    adapter = GameEventPlatformAdapter()
    res = adapter.process_game_event({"event_type": "background_click", "session_id": "s1", "reportable": False, "payload": {}})
    assert res["platform_mocked"] is False
    assert adapter.platform_message_count == 0


def test_target_and_background_map_to_expected_indexes() -> None:
    adapter = GameEventPlatformAdapter()
    t = {"event_type": "target_click", "session_id": "s1", "created_at_ms": 1, "reportable": True, "payload": {"target_index": 0, "action_name": "target_primary"}}
    b = {"event_type": "target_click", "session_id": "s1", "created_at_ms": 2, "reportable": True, "payload": {"target_index": 1, "action_name": "background"}}
    adapter.process_game_event(t)
    adapter.process_game_event(b)
    assert adapter.sender.messages[0]["type"] == "ipc_mouse_data"
    assert adapter.sender.messages[0]["index"] == 0
    assert adapter.sender.messages[1]["index"] == 1


def test_no_session_id_skips_platform_mock() -> None:
    adapter = GameEventPlatformAdapter()
    res = adapter.process_game_event({"event_type": "target_click", "session_id": "", "created_at_ms": 1, "reportable": True, "payload": {"target_index": 0}})
    assert res["reason"] == "no_session_context"
    assert adapter.platform_message_count == 0


def test_core_control_routes_to_platform_mock(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "cc.db"), source_mode="core_control")
    source.apply_session_summary({"session_id": "sid_1", "game_id": "fake_game"})
    target = source.handle_event("target_click", {"x_norm": 0.5, "y_norm": 0.5, "button": 0, "hit": True})
    background = source.handle_event("background_click", {"x_norm": 0.1, "y_norm": 0.1, "button": 1, "hit": False})
    assert target["platform_message_count"] >= 1
    assert target["result"] == "game_event_recorded_and_platform_mocked"
    assert target["last_platform_message"]["index"] == 0
    assert background["last_platform_message"]["index"] == 1
    source.close()


def test_readonly_does_not_generate_platform_message(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "ro.db"), source_mode="core_readonly")
    res = source.handle_event("target_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert res["reason"] == "readonly_ignored"
    assert "platform_message_count" not in res
    source.close()


def test_core_control_without_session_returns_no_session_context_result(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "nosid.db"), source_mode="core_control")
    res = source.handle_event("target_click", {"x_norm": 0.5, "y_norm": 0.5, "button": 0, "hit": True})
    assert res["result"] == "game_event_recorded_no_session_context"
    assert res["platform_message_count"] == 0
    source.close()
