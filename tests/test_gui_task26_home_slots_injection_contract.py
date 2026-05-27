from __future__ import annotations

import json
from pathlib import Path

import pytest

from gui.desktop_model import (
    build_home_card_slots_injection_payload_from_examples,
    expected_home_slot_injection_fields,
    expected_home_slot_qml_properties,
    validate_home_slot_injection_payload,
)


def test_expected_fields_non_empty() -> None:
    fields = expected_home_slot_injection_fields()
    assert fields
    assert "slot_count" in fields


def test_payload_from_examples_and_validate_passes() -> None:
    payload = build_home_card_slots_injection_payload_from_examples(Path("."))
    validate_home_slot_injection_payload(payload)
    assert "slot_count" in payload
    assert "slot1_card_id" in payload
    assert "slot4_card_id" in payload
    assert payload["slot1_card_id"] == "runtime_io_card"
    assert isinstance(payload["slot1_action_ids_text"], str)


def test_missing_field_fails() -> None:
    payload = build_home_card_slots_injection_payload_from_examples(Path("."))
    del payload["slot1_card_id"]
    with pytest.raises(ValueError):
        validate_home_slot_injection_payload(payload)


def test_wrong_required_type_fails() -> None:
    payload = build_home_card_slots_injection_payload_from_examples(Path("."))
    payload["slot1_required"] = "true"
    with pytest.raises(ValueError):
        validate_home_slot_injection_payload(payload)


def test_wrong_widget_count_type_fails() -> None:
    payload = build_home_card_slots_injection_payload_from_examples(Path("."))
    payload["slot1_widget_count"] = "3"
    with pytest.raises(ValueError):
        validate_home_slot_injection_payload(payload)


def test_injection_json_can_load_and_validate() -> None:
    p = Path("assets/layouts/task26_examples/home_desktop_render_model_slots_injection.example.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    validate_home_slot_injection_payload(data)


def test_qml_property_mapping_tokens_exist_for_slot1_to_slot4() -> None:
    qml = Path("ui_qml/components/HomeCardSlotsPreview.qml").read_text(encoding="utf-8")
    for i in range(1, 5):
        for token in [
            f"slot{i}CardId",
            f"slot{i}CardType",
            f"slot{i}RectText",
            f"slot{i}ActionIdsText",
            f"slot{i}SourceRootsText",
            f"slot{i}FirstWidgetLabelsText",
        ]:
            assert token in qml


def test_expected_qml_properties_exist_in_home_card_slots_preview() -> None:
    qml = Path("ui_qml/components/HomeCardSlotsPreview.qml").read_text(encoding="utf-8")
    expected = expected_home_slot_qml_properties()
    for token in expected:
        assert token in qml


def test_developer_lab_passes_key_slot_props() -> None:
    qml = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    for token in [
        "slot1CardId",
        "slot2CardId",
        "slot3CardId",
        "slot4CardId",
        "slot1RectText",
        "slot1ActionIdsText",
        "slot1SourceRootsText",
        "slot1FirstWidgetLabelsText",
    ]:
        assert token in qml


def test_no_banned_tokens_in_slot_qml_files() -> None:
    banned = ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest", "JSON.parse", "File", "read"]
    for path in [
        Path("ui_qml/components/HomeCardSlotsPreview.qml"),
        Path("ui_qml/pages/DeveloperLabPage.qml"),
    ]:
        text = path.read_text(encoding="utf-8")
        for token in banned:
            assert token not in text
