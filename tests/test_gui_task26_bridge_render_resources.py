from __future__ import annotations

import json

import pytest

from gui.desktop_model import validate_home_slot_injection_payload
from gui.gui_facade import GuiFacade

PySide6 = pytest.importorskip("PySide6")

from gui.gui_bridge import GuiBridge


def test_facade_render_resources_contains_task26_home_slots_payload() -> None:
    facade = GuiFacade(mode="mock")
    resources = facade.get_render_resources()
    assert isinstance(resources, dict)
    assert "task26_home_slots_payload" in resources
    assert "task26_home_slots_status" in resources
    payload = resources["task26_home_slots_payload"]
    validate_home_slot_injection_payload(payload)


def test_bridge_render_resources_json_contains_task26_home_slots_payload() -> None:
    facade = GuiFacade(mode="mock")
    bridge = GuiBridge(facade)
    raw = bridge.renderResourcesJson
    data = json.loads(raw)
    assert "task26_home_slots_payload" in data
    payload = data["task26_home_slots_payload"]
    validate_home_slot_injection_payload(payload)
    assert payload["slot1_card_id"] == "runtime_io_card"
