from __future__ import annotations

import json
from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _load_calibration_desktop_json() -> dict:
    return json.loads(_read("assets/layouts/task26_examples/calibration_page.desktop_demo.json"))


def _cards_by_id(data: dict) -> dict[str, dict]:
    return {str(card.get("id", "")): card for card in data.get("cards", [])}


def _collect_action_ids(data: dict) -> set[str]:
    return {
        str(widget.get("action_id"))
        for card in data.get("cards", [])
        for widget in card.get("widgets", [])
        if isinstance(widget, dict) and widget.get("action_id")
    }


def _find_card_index(payload: dict, card_id: str) -> int | None:
    for i in range(1, int(payload.get("card_count", 0)) + 1):
        if payload.get(f"card{i}_id") == card_id:
            return i
    return None


def _find_widget_index(payload: dict, card_index: int, *, widget_id: str | None = None, widget_type: str | None = None) -> int | None:
    for j in range(1, 12):
        if widget_id is not None and payload.get(f"card{card_index}_widget{j}_id") == widget_id:
            return j
        if widget_type is not None and payload.get(f"card{card_index}_widget{j}_type") == widget_type:
            return j
    return None


def test_calibration_desktop_json_uses_formal_three_card_structure() -> None:
    data = _load_calibration_desktop_json()
    cards = _cards_by_id(data)

    assert {
        "calibration_control_card",
        "calibration_feedback_card",
        "calibration_query_card",
    }.issubset(cards)

    # H-6E formal UI removed the older six equal-card pilot structure.
    for legacy_card_id in [
        "calibration_status_card",
        "calibration_actions_card",
        "calibration_detail_card",
        "calibration_progress_card",
        "calibration_selector_card",
        "calibration_guidance_card",
    ]:
        assert legacy_card_id not in cards

    feedback = cards["calibration_feedback_card"]
    assert feedback.get("required") is True
    assert feedback.get("locked") is True
    assert feedback.get("position", {}).get("col_span", 0) >= 6
    assert feedback.get("position", {}).get("row_span", 0) >= 4


def test_calibration_required_actions_are_kept_in_formal_cards() -> None:
    data = _load_calibration_desktop_json()
    actions = _collect_action_ids(data)

    assert {
        "calibration.status",
        "calibration.latest",
        "calibration.list",
        "calibration.start",
        "calibration.show",
        "calibration.bind",
        "calibration.poll",
        "calibration.cancel",
    }.issubset(actions)


def test_calibration_query_is_current_user_scoped_without_user_input() -> None:
    data = _load_calibration_desktop_json()
    query_card = _cards_by_id(data)["calibration_query_card"]
    widgets = query_card.get("widgets", [])

    widget_ids = {w.get("id") for w in widgets if isinstance(w, dict)}
    widget_types = {w.get("type") for w in widgets if isinstance(w, dict)}
    action_ids = {w.get("action_id") for w in widgets if isinstance(w, dict)}

    assert "selected_calibration_id" in widget_ids
    assert "manual_calibration_id" in widget_ids
    assert "select" in widget_types
    assert "input" in widget_types
    assert "calibration.show" in action_ids
    assert "calibration.list" in action_ids
    assert "calibration.latest" in action_ids

    # User selection belongs to User page. Calibration page should not duplicate it.
    assert "calibration_user_id" not in widget_ids
    assert "selected_user_id" not in widget_ids


def test_calibration_layout_resource_exposes_query_select_options() -> None:
    from gui.desktop_model import build_calibration_layout_render_resource, validate_desktop_layout_preview_payload

    payload = build_calibration_layout_render_resource(Path("."))["task26_calibration_layout_payload"]
    validate_desktop_layout_preview_payload(payload)

    query_index = _find_card_index(payload, "calibration_query_card")
    assert query_index is not None

    selector_widget = _find_widget_index(payload, query_index, widget_id="selected_calibration_id")
    assert selector_widget is not None
    assert payload[f"card{query_index}_widget{selector_widget}_type"] == "select"
    options_text = str(payload.get(f"card{query_index}_widget{selector_widget}_options_text", ""))
    assert "manual" in options_text


def test_calibration_feedback_card_exposes_complete_formal_source_contract() -> None:
    from gui.desktop_model import build_calibration_layout_render_resource, validate_desktop_layout_preview_payload

    payload = build_calibration_layout_render_resource(Path("."))["task26_calibration_layout_payload"]
    validate_desktop_layout_preview_payload(payload)

    feedback_index = _find_card_index(payload, "calibration_feedback_card")
    assert feedback_index is not None

    sources = {
        str(payload.get(f"card{feedback_index}_widget{j}_source", ""))
        for j in range(1, 12)
        if str(payload.get(f"card{feedback_index}_widget{j}_source", ""))
    }
    assert {
        "controlStateJson.calibration_progress_running",
        "controlStateJson.calibration_progress_phase",
        "controlStateJson.calibration_progress_elapsed_sec",
        "controlStateJson.calibration_phase_remaining_sec",
        "controlStateJson.calibration_progress_percent",
        "controlStateJson.calibration_operator_guidance",
    }.issubset(sources)


def test_gui_facade_exposes_calibration_context_for_formal_page() -> None:
    from gui.gui_facade import GuiFacade

    resources = GuiFacade(mode="core-control", db_path="data/relic_local.db", user_id="TEST").get_render_resources()
    assert resources.get("task26_calibration_context_status") == "ok"
    context = resources.get("task26_calibration_context")
    assert isinstance(context, dict)
    assert "last_calibration_id" in context
    assert "calibration_phase" in context
    assert "calibration_running" in context

    payload = resources.get("task26_calibration_layout_payload")
    assert isinstance(payload, dict)
    assert payload.get("card_count", 0) >= 3


def test_calibration_progress_guidance_is_finite_and_cancelable() -> None:
    from gui.gui_facade import GuiFacade
    import time

    facade = GuiFacade(mode="core-control", db_path="data/relic_local.db", user_id="TEST")
    start = facade.invoke_action("calibration.start", {"user_id": "TEST"})
    progress = start.get("progress") or {}
    assert progress.get("running") is True
    assert progress.get("current_phase") == "phase 1/4"
    assert progress.get("remaining_sec") not in (None, "", "n/a")

    facade._calibration_started_at_ms = int(time.time() * 1000) - sum(facade._calibration_phase_durations_ms()) - 250
    completed = facade._calibration_progress_summary()
    assert completed.get("running") is False
    assert completed.get("status") == "idle"
    assert completed.get("current_phase") == "n/a"

    facade.invoke_action("calibration.start", {"user_id": "TEST"})
    cancelled = facade.invoke_action("calibration.cancel", {"user_id": "TEST"})
    assert cancelled.get("status") == "cancelled"
    after_cancel = facade.invoke_action("calibration.poll", {"user_id": "TEST"})
    assert (after_cancel.get("progress") or {}).get("running") is False
    assert (after_cancel.get("progress") or {}).get("status") == "idle"



def test_calibration_context_preserves_full_prompt_and_timer_fields() -> None:
    from gui.gui_facade import GuiFacade

    facade = GuiFacade(mode="core-control", db_path="data/relic_local.db", user_id="TEST")
    context = facade.get_render_resources()["task26_calibration_context"]
    for key in [
        "calibration_progress_status",
        "calibration_progress_running",
        "calibration_running",
        "calibration_progress_phase",
        "calibration_phase",
        "calibration_progress_elapsed_sec",
        "calibration_phase_remaining_sec",
        "calibration_total_remaining_sec",
        "calibration_progress_fraction",
        "calibration_progress_percent",
        "calibration_phase_prompt_text",
        "calibration_operator_guidance",
        "calibration_phase_title",
        "calibration_phase_instruction",
        "calibration_phase_avoid_instruction",
        "calibration_phase_duration_hint",
    ]:
        assert key in context

    assert "phase 1/4" in str(context.get("calibration_phase_prompt_text", ""))
    assert "phase 4/4" in str(context.get("calibration_phase_prompt_text", ""))


def test_calibration_page_refreshes_desktop_feedback_from_bridge_timer() -> None:
    text = _read("ui_qml/pages/CalibrationPage.qml")
    assert "calibrationProgressTimer" in text
    assert "refreshDesktopCalibrationFeedback" in text
    assert "calibrationProgressIsRunning" in text
    assert 'guiBridge.invokeAction("calibration.poll", "{}")' in text
    assert "root.controlStateObj = safeJsonParse(root.guiBridge.controlStateJson)" in text
    assert "root.renderResourcesObj = safeJsonParse(root.guiBridge.renderResourcesJson)" in text

def test_calibration_detail_popup_declares_only_calibration_fields() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "Latest Calibration Detail" in _read("assets/layouts/task26_examples/calibration_page.desktop_demo.json")
    assert "actionId === \"calibration.latest\"" in text
    assert "Current guidance:" not in text
    assert "calibration_phase_instruction" not in text.split("id: calibrationPopup", 1)[1]
    for token in [
        "device_id",
        "attention_valid_sample_ratio",
        "gyro_bias_x",
        "gyro_noise_x",
        "gyro_stability_score",
        "signal_quality_baseline",
    ]:
        assert token in text


def test_calibration_live_process_timer_has_nonzero_remaining_at_start() -> None:
    from gui.gui_facade import GuiFacade
    import time

    class _RunningProcess:
        def poll(self):
            return None

    facade = GuiFacade(mode="core-control", db_path="data/relic_local.db", user_id="TEST")
    facade._calibration_process = _RunningProcess()
    facade._calibration_user_id = "TEST"
    facade._calibration_started_at_ms = int(time.time() * 1000)
    facade._calibration_exit_code = None
    facade._calibration_current_phase = "phase 1/4"
    progress = facade._calibration_progress_summary()

    assert progress.get("running") is True
    assert progress.get("process_running") is True
    assert progress.get("current_phase") == "phase 1/4"
    assert float(progress.get("remaining_sec", 0)) > 0
    assert float(progress.get("total_remaining_sec", 0)) > 0


def test_calibration_user_binding_safety_contract_is_declared() -> None:
    text = _read("gui/gui_facade.py")
    assert "calibration_user_mismatch" in text
    assert "detail_user_id" in text
    assert "TEST_NEW" not in _read("assets/layouts/task26_examples/calibration_page.desktop_demo.json")
    assert "user_id\") if \"user_id\" in payload else (self._current_user_override" in text


def test_auto_calibration_type_resolves_first_profile_for_new_users() -> None:
    text = _read("gui/gui_facade.py")
    assert "calibration_type == \"auto\"" in text
    assert "first_profile" in text
    assert "quick_check" in text
    assert "profile_loaded" in text
    assert "last_calibration_id" in text


def test_calibration_list_and_selector_do_not_fallback_to_polluted_profile_binding() -> None:
    text = _read("gui/gui_facade.py")
    assert "Never fall back to profile.last_calibration_id" in text
    assert "Do not insert controlStateJson.last_calibration_id" in text
    assert "binding_inconsistent" in text

    data = _load_calibration_desktop_json()
    cards = _cards_by_id(data)
    for card_id in ["calibration_control_card", "calibration_query_card"]:
        card = cards[card_id]
        for widget in card.get("widgets", []):
            if widget.get("id") == "selected_calibration_id":
                assert widget.get("options") == ["manual"]
                assert widget.get("value") == "manual"
                assert widget.get("fallback") == "manual"


def test_calibration_bind_rejects_cross_user_detail_before_writing_profile() -> None:
    from gui.gui_facade import GuiFacade

    facade = GuiFacade(mode="mock", db_path="data/relic_local.db", user_id="TEST_NEW")
    facade._fetch_calibration_detail = lambda calibration_id: {
        "status": "accepted",
        "message": "calibration_loaded",
        "calibration_id": calibration_id,
        "user_id": "TEST",
        "valid": True,
    }

    result = facade._bind_calibration_summary("TEST_NEW", "cal_owned_by_test")
    assert result["status"] == "calibration_user_mismatch"
    assert result["accepted"] is False
    assert result["calibration_user_id"] == "TEST"


def test_calibration_options_ignore_polluted_bound_profile_when_user_has_no_records() -> None:
    from gui.gui_facade import GuiFacade

    facade = GuiFacade(mode="mock", db_path="data/relic_local.db", user_id="TEST_NEW")
    facade._fetch_calibration_list = lambda user_id: {
        "status": "accepted",
        "items": [],
        "calibrations": [],
        "items_count": 0,
        "calibration_count": 0,
    }
    facade._fetch_calibration_status = lambda user_id: {
        "status": "binding_inconsistent",
        "last_calibration_id": "cal_test_only",
        "calibration_user_id": "TEST",
        "calibration_usable": False,
    }

    options_text, selected = facade._calibration_options_text_for_user("TEST_NEW")
    assert options_text == "manual"
    assert selected == "manual"


def test_card_action_args_attach_current_user_even_when_widget_args_exist() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "always attach the current GUI user" in text
    assert 'resolved.indexOf("\\\"user_id\\\"")' in text
    assert 'jsonEscapeText(currentUser)' in text
