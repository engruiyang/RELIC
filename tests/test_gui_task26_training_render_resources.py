from __future__ import annotations

import json

import pytest

from gui.desktop_model import validate_training_slot_injection_payload
from gui.gui_facade import GuiFacade


def _assert_training_slots_payload(payload: dict) -> None:
    validate_training_slot_injection_payload(payload)
    assert payload["slot_count"] == 7
    assert "game_canvas_card" in {payload[f"slot{i}_card_id"] for i in range(1, 8)}


def test_facade_render_resources_contains_training_summary_and_slots() -> None:
    resources = GuiFacade(mode="mock").get_render_resources()
    assert resources["task26_training_status"] == "ok"
    summary = resources["task26_training_summary"]
    assert summary["page_id"] == "training"
    assert summary["safe_stop_present"] is True
    assert "training_control_card" in summary["required_card_ids"]
    assert "placeholder" in summary["game_canvas_card_status"]
    assert resources["task26_training_slots_status"] == "ok"
    assert "task26_training_slots_payload" in resources
    _assert_training_slots_payload(resources["task26_training_slots_payload"])


def test_bridge_render_resources_json_contains_training_summary_and_slots() -> None:
    pytest.importorskip("PySide6")
    from gui.gui_bridge import GuiBridge

    bridge = GuiBridge(GuiFacade(mode="mock"))
    data = json.loads(bridge.renderResourcesJson)
    assert data["task26_training_status"] == "ok"
    assert "task26_training_summary" in data
    summary = data["task26_training_summary"]
    assert summary["page_id"] == "training"
    assert summary["safe_stop_present"] is True
    assert data["task26_training_slots_status"] == "ok"
    assert "task26_training_slots_payload" in data
    _assert_training_slots_payload(data["task26_training_slots_payload"])
