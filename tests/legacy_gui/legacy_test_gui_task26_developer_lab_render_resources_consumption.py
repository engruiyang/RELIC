from __future__ import annotations

import json
from pathlib import Path

import pytest

from gui.desktop_model import validate_home_slot_injection_payload
from gui.gui_facade import GuiFacade


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_developer_lab_consumes_render_resources_payload_tokens() -> None:
    text = _read("ui_qml/pages/DeveloperLabPage.qml")
    for token in [
        "task26_home_slots_payload",
        "task26PayloadValue",
        "renderResourcesObj",
        "HomeCardSlotsPreview",
        "TASK26 Home Card Slots Preview",
    ]:
        assert token in text


def test_developer_lab_home_slots_props_come_from_payload() -> None:
    text = _read("ui_qml/pages/DeveloperLabPage.qml")
    for token in [
        'slot1CardId: task26PayloadValue("slot1_card_id"',
        'slot2CardId: task26PayloadValue("slot2_card_id"',
        'slot3CardId: task26PayloadValue("slot3_card_id"',
        'slot4CardId: task26PayloadValue("slot4_card_id"',
        'slot1RectText: task26PayloadValue("slot1_rect_text"',
        'slot1ActionIdsText: task26PayloadValue("slot1_action_ids_text"',
        'slot1SourceRootsText: task26PayloadValue("slot1_source_roots_text"',
        'slot1FirstWidgetLabelsText: task26PayloadValue("slot1_first_widget_labels_text"',
    ]:
        assert token in text


def test_developer_lab_no_banned_runtime_or_file_tokens() -> None:
    text = _read("ui_qml/pages/DeveloperLabPage.qml")
    for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest", "File", "read"]:
        assert token not in text


def test_home_and_training_do_not_consume_task26_slots() -> None:
    for path in ["ui_qml/pages/HomePage.qml", "ui_qml/pages/TrainingPage.qml"]:
        text = _read(path)
        for token in ["task26_home_slots_payload", "HomeCardSlotsPreview", "task26PayloadValue"]:
            assert token not in text


def test_facade_render_resources_still_exposes_task26_payload() -> None:
    resources = GuiFacade(mode="mock").get_render_resources()
    assert resources["task26_home_slots_status"] == "ok"
    payload = resources["task26_home_slots_payload"]
    validate_home_slot_injection_payload(payload)
    assert payload["slot1_card_id"] == "runtime_io_card"


def test_bridge_render_resources_json_still_exposes_task26_payload() -> None:
    pytest.importorskip("PySide6")
    from gui.gui_bridge import GuiBridge

    bridge = GuiBridge(GuiFacade(mode="mock"))
    data = json.loads(bridge.renderResourcesJson)
    assert data["task26_home_slots_status"] == "ok"
    payload = data["task26_home_slots_payload"]
    validate_home_slot_injection_payload(payload)
    assert payload["slot1_card_id"] == "runtime_io_card"
