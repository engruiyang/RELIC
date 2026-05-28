from __future__ import annotations

import json
from pathlib import Path

import pytest

from gui.desktop_model import (
    build_training_card_slots,
    build_training_card_slots_injection_payload,
    expected_training_slot_injection_fields,
    validate_training_slot_injection_payload,
)

ROOT = Path(".")
INJECTION_PATH = ROOT / "assets" / "layouts" / "task26_examples" / "training_desktop_render_model_slots_injection.example.json"


def _payload() -> dict:
    return build_training_card_slots_injection_payload(build_training_card_slots(ROOT))


def test_expected_training_slot_injection_fields_non_empty() -> None:
    assert expected_training_slot_injection_fields()


def test_build_training_slots_and_payload_contract() -> None:
    slots = build_training_card_slots(ROOT)
    assert len(slots) == 7
    payload = build_training_card_slots_injection_payload(slots)
    assert payload["slot_count"] == 7
    validate_training_slot_injection_payload(payload)
    assert payload["slot1_card_id"] == "training_control_card"
    assert "game_canvas_card" in {payload[f"slot{i}_card_id"] for i in range(1, 8)}


def test_training_payload_validation_rejects_missing_field() -> None:
    payload = _payload()
    del payload["slot1_card_id"]
    with pytest.raises(ValueError, match="slot1_card_id"):
        validate_training_slot_injection_payload(payload)


def test_training_payload_validation_rejects_required_type() -> None:
    payload = _payload()
    payload["slot1_required"] = "true"
    with pytest.raises(ValueError, match="slot1_required"):
        validate_training_slot_injection_payload(payload)


def test_training_payload_validation_rejects_widget_count_type() -> None:
    payload = _payload()
    payload["slot1_widget_count"] = "5"
    with pytest.raises(ValueError, match="slot1_widget_count"):
        validate_training_slot_injection_payload(payload)


def test_generated_training_slots_injection_json_validates() -> None:
    data = json.loads(INJECTION_PATH.read_text(encoding="utf-8"))
    validate_training_slot_injection_payload(data)
    assert data["slot_count"] == 7


def test_training_payload_contains_safe_actions_and_canvas_placeholder() -> None:
    payload = _payload()
    action_text = " | ".join(payload[f"slot{i}_action_ids_text"] for i in range(1, 8))
    assert "live.safe_stop" in action_text or "session.start" in action_text
    canvas_slots = [i for i in range(1, 8) if payload[f"slot{i}_card_id"] == "game_canvas_card"]
    assert canvas_slots
    idx = canvas_slots[0]
    assert payload[f"slot{idx}_placeholder"] is True or payload[f"slot{idx}_role"] == "game_canvas_placeholder"
