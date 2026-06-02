from gui.gui_facade import GuiFacade


def test_gui_facade_records_pointer_and_hit_for_target_click() -> None:
    facade = GuiFacade(mode="mock")
    facade.handle_gui_event(
        "target_click",
        {"x_norm": 0.5, "y_norm": 0.5, "hit": True, "source": "minimal_game_canvas"},
    )
    assert facade.event_count == 1
    assert facade.last_event["event_type"] == "target_click"
    assert facade.last_pointer_x == 0.5
    assert facade.last_pointer_y == 0.5
    assert facade.last_hit_state is True


def test_gui_facade_records_background_click_hit_false() -> None:
    facade = GuiFacade(mode="mock")
    facade.handle_gui_event(
        "background_click",
        {"x_norm": 0.12, "y_norm": 0.8, "hit": False, "source": "minimal_game_canvas"},
    )
    assert facade.event_count == 1
    assert facade.last_event["event_type"] == "background_click"
    assert facade.last_hit_state is False


def test_modes_keep_event_result_contract(tmp_path) -> None:
    core = GuiFacade(mode="core", db_path=str(tmp_path / "relic_ro.db"))
    core.handle_gui_event("target_click", {"x_norm": 0.5, "y_norm": 0.5, "hit": True})
    assert core.last_event_result["reason"] == "readonly_ignored"

    control = GuiFacade(mode="core-control", db_path=str(tmp_path / "relic_cc.db"))
    control.handle_gui_event("target_click", {"x_norm": 0.5, "y_norm": 0.5, "hit": True})
    assert control.last_event_result["reason"] == "game_event_recorded_no_session_context"
