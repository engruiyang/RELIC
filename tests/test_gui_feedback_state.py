from __future__ import annotations

from gui.gui_facade import GuiFacade


def test_show_profile_missing_user_and_test_user_paths(tmp_path) -> None:
    db = tmp_path / "relic.db"
    f = GuiFacade(mode="core-control", db_path=str(db), user_id="")
    r = f.invoke_action("user.show_profile", {})
    assert r["status"] in {"missing_user", "user_not_found", "profile_not_found"}
    f.close()


def test_session_state_fields_exist() -> None:
    f = GuiFacade(mode="live-control", user_id="TEST")
    cs = f.get_control_state()
    for k in ["session_active", "current_session_id", "session_elapsed_ms", "latest_report_path", "last_session_status"]:
        assert k in cs
    f.close()


def test_calibration_status_feedback() -> None:
    f = GuiFacade(mode="core-control", user_id="TEST")
    r = f.invoke_action("calibration.start", {})
    assert r["status"] == "not_implemented"
    r2 = f.invoke_action("calibration.status", {})
    assert r2["status"] in {"missing_user", "no_calibration", "profile_without_calibration", "accepted"}
    f.close()
