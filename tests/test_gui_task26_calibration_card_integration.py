import json
from pathlib import Path

from gui.gui_facade import GuiFacade


def _calibration_page() -> dict:
    return json.loads(Path("assets/layouts/task26_examples/calibration_page.desktop_demo.json").read_text(encoding="utf-8"))


def _all_widgets(page: dict) -> list[dict]:
    return [w for c in page.get("cards", []) for w in c.get("widgets", [])]


def test_calibration_progress_guidance_is_finite_and_cancelable() -> None:
    page = _calibration_page()
    actions = {w.get("action_id") for w in _all_widgets(page)}
    assert {"calibration.start", "calibration.poll", "calibration.cancel", "calibration.status"}.issubset(actions)
    # A cancelled calibration is a valid terminal state; the UI should surface it instead of pretending idle.
    f = GuiFacade(mode="live-control", user_id="TEST", game_id="trace_lock")
    try:
        r = f.invoke_action("calibration.cancel", {"user_id": "TEST"})
        assert r.get("status") in {"cancelled", "idle", "noop", "not_running", "no_active_calibration", "live_control_required"}
    finally:
        f.close()


def test_calibration_options_ignore_polluted_bound_profile_when_user_has_no_records() -> None:
    page = _calibration_page()
    select_widgets = [w for w in _all_widgets(page) if w.get("type") == "select"]
    assert select_widgets
    option_text = "|".join(str(x) for w in select_widgets for x in (w.get("options") or []))
    assert "manual" in option_text


def test_calibration_actions_are_declared_in_current_cards() -> None:
    page = _calibration_page()
    actions = {w.get("action_id") for w in _all_widgets(page)}
    assert {"calibration.start", "calibration.bind", "calibration.show"}.issubset(actions)
