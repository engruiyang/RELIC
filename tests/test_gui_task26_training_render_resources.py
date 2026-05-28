from __future__ import annotations

import json

import pytest

from gui.gui_facade import GuiFacade


def test_facade_render_resources_contains_training_summary() -> None:
    resources = GuiFacade(mode="mock").get_render_resources()
    assert resources["task26_training_status"] == "ok"
    summary = resources["task26_training_summary"]
    assert summary["page_id"] == "training"
    assert summary["safe_stop_present"] is True
    assert "training_control_card" in summary["required_card_ids"]
    assert "placeholder" in summary["game_canvas_card_status"]


def test_bridge_render_resources_json_contains_training_summary() -> None:
    pytest.importorskip("PySide6")
    from gui.gui_bridge import GuiBridge

    bridge = GuiBridge(GuiFacade(mode="mock"))
    data = json.loads(bridge.renderResourcesJson)
    assert data["task26_training_status"] == "ok"
    assert "task26_training_summary" in data
    summary = data["task26_training_summary"]
    assert summary["page_id"] == "training"
    assert summary["safe_stop_present"] is True
