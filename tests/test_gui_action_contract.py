from __future__ import annotations

from gui.gui_facade import GuiFacade


def _manifest_map(facade: GuiFacade) -> dict[str, dict]:
    return {x["action_id"]: x for x in facade.get_control_manifest()}


def test_manifest_truth_by_mode() -> None:
    mock = _manifest_map(GuiFacade(mode="mock"))
    ro = _manifest_map(GuiFacade(mode="live-readonly"))
    lc = _manifest_map(GuiFacade(mode="live-control"))
    assert mock["live.reconnect"]["supported"] is False
    assert ro["session.start"]["enabled"] is False
    assert ro["session.start"]["readonly_allowed"] is False
    assert lc["live.safe_stop"]["supported"] is True


def test_readonly_and_unsupported_feedback() -> None:
    f = GuiFacade(mode="live-readonly")
    r1 = f.invoke_action("session.start", {})
    assert r1["status"] == "readonly_not_allowed"
    r2 = f.invoke_action("calibration.start", {})
    assert r2["status"] == "not_implemented"
    assert f.get_control_state()["last_command_error"] in {"readonly_not_allowed", "not_implemented"}
    f.close()


def test_profile_and_calibration_missing_user_feedback() -> None:
    f = GuiFacade(mode="live-readonly")
    assert f.invoke_action("user.show_profile", {})["status"] == "missing_user"
    assert f.invoke_action("calibration.status", {})["status"] == "missing_user"
    f.close()


def test_control_state_updates_after_actions() -> None:
    f = GuiFacade(mode="mock")
    c0 = f.get_control_state()["command_count"]
    f.invoke_action("app.refresh_now", {})
    c1 = f.get_control_state()["command_count"]
    assert c1 > c0
    assert f.get_control_state()["last_command"] == "refresh_snapshot" or f.get_control_state()["last_command"] == "app.refresh_now"


def test_live_control_session_state_transition() -> None:
    f = GuiFacade(mode="live-control")
    r = f.invoke_action("session.start", {})
    assert r["status"] in {"training_started", "conflict"}
    s = f.get_control_state()
    if r["status"] == "training_started":
        assert s["session_active"] is True
        assert s["current_session_id"]
    r2 = f.invoke_action("session.stop", {})
    assert r2["status"] in {"training_completed", "training_stopped", "noop"}
    s2 = f.get_control_state()
    assert s2["session_active"] is False or r2["status"] == "training_stopped"
    f.close()


def test_no_demo_loaded_message_for_test_user():
    f = GuiFacade(mode="live-control", user_id="TEST")
    r = f.invoke_action("user.load_current", {})
    assert "demo_user_loaded" not in str(r)
    f.close()
