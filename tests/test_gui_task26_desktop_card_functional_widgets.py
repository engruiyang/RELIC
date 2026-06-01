from pathlib import Path

from gui.desktop_model import build_home_layout_preview_payload, build_training_layout_preview_payload


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_card_preview_declares_six_widget_slots_and_action_ids() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    for idx in range(1, 7):
        assert f"widget{idx}Type" in text
        assert f"widget{idx}ActionId" in text
    assert "function sourceValue" in text
    assert "eval" not in text
    # Loader is now intentionally allowed for the game_canvas card only, so
    # non-game cards do not create hidden GameCanvas instances.
    for token in ["Repeater", "Timer", "subprocess", "XMLHttpRequest"]:
        assert token not in text
    assert "Loader" in text
    assert "isGameCanvasCard" in text


def test_layout_preview_accepts_runtime_objects_for_cards() -> None:
    text = _read("ui_qml/components/DesktopLayoutPreview.qml")
    for token in ["guiBridge", "runtimeSnapshotObj", "sessionStateObj", "controlStateObj", "gameHudObj"]:
        assert token in text


def test_layout_payload_contains_flat_widget_fields() -> None:
    payload = build_home_layout_preview_payload(Path("."))
    assert "card1_widget1_type" in payload
    assert "card1_widget1_label" in payload
    assert "card1_widget1_action_id" in payload
    assert isinstance(payload["card1_widget1_required"], bool)


def test_home_runtime_io_card_has_text_or_metric_widgets() -> None:
    payload = build_home_layout_preview_payload(Path("."))
    assert payload["card1_id"] == "runtime_io_card"
    types = {payload[f"card1_widget{i}_type"] for i in range(1, 7)}
    assert types & {"text", "metric"}


def test_training_control_card_has_button_widget_and_safe_stop_action() -> None:
    payload = build_training_layout_preview_payload(Path("."))
    control_index = next(i for i in range(1, 8) if payload[f"card{i}_id"] == "training_control_card")
    types = {payload[f"card{control_index}_widget{i}_type"] for i in range(1, 7)}
    actions = {payload[f"card{control_index}_widget{i}_action_id"] for i in range(1, 7)}
    assert "button" in types
    assert "live.safe_stop" in actions
