from gui.gui_core_source import GuiCoreSnapshotSource


def test_core_control_target_click_routes_to_game_client(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "r.db"), source_mode="core_control")
    result = source.handle_event("target_click", {"x_norm": 0.5, "y_norm": 0.5, "hit": False, "button": 0, "source": "minimal_game_canvas"})
    assert result["result"] == "game_event_recorded_no_session_context"
    assert result["game_input"]["x_norm"] == 0.5
    assert result["game_input"]["y_norm"] == 0.5
    assert result["game_input"]["debug_hit"] is False
    assert result["last_game_event"]["event_type"] == "target_click"
    payload = result["last_game_event"]["payload"]
    assert payload["target_index"] == 0
    assert payload["action_name"] == "target_primary"
    assert result["game_event_count"] >= 1
    assert result["last_game_view_summary"]["entity_count"] >= 1
    source.close()


def test_core_control_background_click_routes_to_game_client(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "r2.db"), source_mode="core_control")
    result = source.handle_event("background_click", {"x_norm": 0.1, "y_norm": 0.1, "hit": True, "button": 1, "source": "minimal_game_canvas"})
    assert result["last_game_event"]["event_type"] == "background_click"
    payload = result["last_game_event"]["payload"]
    assert payload["target_index"] == 1
    assert payload["action_name"] == "background"
    source.close()


def test_modes_do_not_route_to_game_client_except_core_control(tmp_path) -> None:
    readonly = GuiCoreSnapshotSource(db_path=str(tmp_path / "ro.db"), source_mode="core_readonly")
    result = readonly.handle_event("target_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert result["reason"] == "readonly_ignored"
    assert "last_game_event" not in result
    readonly.close()


def test_session_switch_updates_platform_mock_session_id(tmp_path) -> None:
    source = GuiCoreSnapshotSource(db_path=str(tmp_path / "sw.db"), source_mode="core_control")
    source.apply_session_summary({"session_id": "sid_first", "game_id": "fake_game"})
    first = source.handle_event("target_click", {"x_norm": 0.5, "y_norm": 0.5, "button": 0, "hit": True})
    assert first["game_input"]["session_id"] == "sid_first"
    assert first["last_game_event"]["session_id"] == "sid_first"
    assert first["last_platform_message"]["session_id"] == "sid_first"
    assert first["result"] == "game_event_recorded_and_platform_mocked"

    source.apply_session_summary({"session_id": "sid_second", "game_id": "fake_game"})
    second = source.handle_event("target_click", {"x_norm": 0.5, "y_norm": 0.5, "button": 0, "hit": True})
    assert second["game_input"]["session_id"] == "sid_second"
    assert second["last_game_event"]["session_id"] == "sid_second"
    assert second["last_platform_message"]["session_id"] == "sid_second"
    assert second["last_platform_message"]["session_id"] != "sid_first"

    bg = source.handle_event("background_click", {"x_norm": 0.1, "y_norm": 0.1, "button": 1, "hit": False})
    assert bg["game_input"]["session_id"] == "sid_second"
    assert bg["last_game_event"]["session_id"] == "sid_second"
    assert bg["last_platform_message"]["session_id"] == "sid_second"
    source.close()
