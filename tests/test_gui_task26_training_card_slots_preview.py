from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


REQUIRED_CARD_TOKENS = [
    "training_control_card",
    "session_card",
    "runtime_io_card",
    "calibration_status_card",
    "game_hud_card",
    "game_canvas_card",
    "diagnostics_summary_card",
]


def test_training_card_slot_preview_components_exist() -> None:
    assert Path("ui_qml/components/TrainingCardSlotPreview.qml").exists()
    assert Path("ui_qml/components/TrainingCardSlotsPreview.qml").exists()


def test_training_card_slots_preview_contains_required_card_tokens() -> None:
    text = _read("ui_qml/components/TrainingCardSlotsPreview.qml")
    assert "Training Card Slots Preview" in text
    for token in REQUIRED_CARD_TOKENS:
        assert token in text


def test_developer_lab_consumes_training_slots_payload() -> None:
    text = _read("ui_qml/pages/DeveloperLabPage.qml")
    for token in [
        "TASK26 Training Card Slots Preview",
        "TrainingCardSlotsPreview",
        "task26TrainingCardSlotsPreview",
        "task26TrainingSlotsPayload",
        "task26TrainingSlotValue",
        "task26_training_slots_payload",
    ]:
        assert token in text


def test_home_and_training_pages_do_not_consume_training_slots_payload() -> None:
    for path in ["ui_qml/pages/HomePage.qml", "ui_qml/pages/TrainingPage.qml"]:
        text = _read(path)
        for token in ["task26_training_slots_payload", "TrainingCardSlotsPreview", "task26TrainingSlotValue"]:
            assert token not in text


def test_training_card_slots_qml_avoids_dynamic_file_and_runtime_tokens() -> None:
    for path in [
        "ui_qml/components/TrainingCardSlotPreview.qml",
        "ui_qml/components/TrainingCardSlotsPreview.qml",
        "ui_qml/pages/DeveloperLabPage.qml",
    ]:
        text = _read(path)
        for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest", "File", "read"]:
            assert token not in text
        assert "JSON.parse" not in text
