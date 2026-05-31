from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from gui.desktop_model import (
    build_page_render_model,
    build_training_card_slots,
    build_training_card_slots_injection_payload,
    build_training_contract_summary,
    build_training_render_model,
    build_training_render_model_summary,
    build_training_slots_render_resource,
    validate_training_slot_injection_payload,
)
from gui.desktop_schema import load_json

ROOT = Path(".")
CONFIG_PATH = ROOT / "assets" / "layouts" / "task26_examples" / "training_page.desktop_demo.json"


def _model() -> dict:
    return build_training_render_model(ROOT)


def _card(model: dict, card_id: str) -> dict:
    cards = {c.get("id"): c for c in model.get("cards", []) if isinstance(c, dict)}
    return cards[card_id]


def _action_ids(model: dict) -> set[str]:
    actions: set[str] = set()
    for card in model.get("cards", []):
        for widget in card.get("widgets", []):
            action_id = widget.get("action_id")
            if isinstance(action_id, str) and action_id:
                actions.add(action_id)
    return actions


def test_build_training_render_model_basic_shape() -> None:
    model = _model()
    assert model["page_id"] == "training"
    assert model["cards"]
    assert _card(model, "training_control_card")
    assert _card(model, "game_canvas_card")
    assert _card(model, "difficulty_control_card")


def test_training_render_cards_have_positive_rects() -> None:
    for card in _model()["cards"]:
        for key in ["x", "y", "width", "height"]:
            assert key in card, card.get("id")
        assert card["width"] > 0, card.get("id")
        assert card["height"] > 0, card.get("id")


def test_training_control_card_locked_and_actions_present() -> None:
    model = _model()
    assert _card(model, "training_control_card")["locked"] is True
    actions = _action_ids(model)
    assert "live.safe_stop" in actions
    assert "session.start" in actions
    assert "session.stop" in actions


def test_build_training_render_model_summary() -> None:
    summary = build_training_render_model_summary(ROOT)
    assert summary["page_id"] == "training"
    assert summary["card_count"] >= 4
    assert "live.safe_stop" in summary["action_ids"] or "session.start" in summary["action_ids"]


def test_non_grid_layout_raises_value_error() -> None:
    config = load_json(CONFIG_PATH)
    bad = deepcopy(config)
    bad["layout"] = dict(bad["layout"])
    bad["layout"]["mode"] = "freeform"
    with pytest.raises(ValueError, match="only grid layout"):
        build_page_render_model(bad)


def test_out_of_grid_boundary_raises_value_error() -> None:
    config = load_json(CONFIG_PATH)
    bad = deepcopy(config)
    bad["cards"][0] = dict(bad["cards"][0])
    bad["cards"][0]["position"] = dict(bad["cards"][0]["position"])
    bad["cards"][0]["position"]["col"] = 12
    bad["cards"][0]["position"]["col_span"] = 2
    with pytest.raises(ValueError, match="out of grid boundary"):
        build_page_render_model(bad)


def test_build_training_contract_summary_guards() -> None:
    summary = build_training_contract_summary(ROOT)
    assert "live.safe_stop" in summary["action_ids"]
    assert any(src.startswith("gameHudJson") for src in summary["placeholder_sources"])
    assert summary["game_canvas_card_status"]
    assert summary["safe_stop_present"] is True
    assert summary["training_slots_supported"] is True
    assert summary["training_injection_supported"] is True


def test_build_training_card_slots_and_injection_payload() -> None:
    slots = build_training_card_slots(ROOT)
    assert len(slots) >= 4
    card_ids = {slot["card_id"] for slot in slots}
    assert "training_control_card" in card_ids
    assert "game_canvas_card" in card_ids
    assert "game_hud_card" in card_ids
    assert "difficulty_control_card" in card_ids
    payload = build_training_card_slots_injection_payload(slots)
    validate_training_slot_injection_payload(payload)
    assert payload["slot_count"] >= 4
    resource = build_training_slots_render_resource(ROOT)
    assert resource["task26_training_slots_status"] == "ok"
    validate_training_slot_injection_payload(resource["task26_training_slots_payload"])
