from __future__ import annotations

import json
from pathlib import Path

from gui.desktop_coverage import validate_action_ids
from gui.desktop_schema import (
    collect_action_ids_from_obj,
    collect_sources_from_obj,
    load_json,
    reject_script_like_values,
    validate_page_config,
    validate_source_roots,
)

ROOT = Path(".")
CONFIG_PATH = ROOT / "assets" / "layouts" / "task26_examples" / "training_page.desktop_demo.json"
REQUIRED_CARDS = {
    "training_control_card",
    "session_card",
    "runtime_io_card",
    "calibration_status_card",
    "game_hud_card",
    "game_canvas_card",
    "diagnostics_summary_card",
}


def _config() -> dict:
    return load_json(CONFIG_PATH)


def _card(config: dict, card_id: str) -> dict:
    cards = {c.get("id"): c for c in config.get("cards", []) if isinstance(c, dict)}
    return cards[card_id]


def _action_ids(card: dict) -> set[str]:
    return {
        w.get("action_id")
        for w in card.get("widgets", [])
        if isinstance(w, dict) and isinstance(w.get("action_id"), str)
    }


def _sources(card: dict) -> set[str]:
    return {
        w.get("source")
        for w in card.get("widgets", [])
        if isinstance(w, dict) and isinstance(w.get("source"), str)
    }


def test_training_page_desktop_demo_exists_and_parses() -> None:
    assert CONFIG_PATH.exists()
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_training_page_rejects_script_like_values() -> None:
    reject_script_like_values(_config())


def test_training_page_id_and_required_cards() -> None:
    config = _config()
    assert config["page_id"] == "training"
    card_ids = {c.get("id") for c in config.get("cards", []) if isinstance(c, dict)}
    assert REQUIRED_CARDS <= card_ids


def test_required_cards_are_locked() -> None:
    for card in _config()["cards"]:
        if card.get("required") is True:
            assert card.get("locked") is True, card.get("id")


def test_training_control_actions_include_session_and_safe_stop() -> None:
    card = _card(_config(), "training_control_card")
    actions = _action_ids(card)
    assert {"session.start", "session.stop", "live.safe_stop"} <= actions


def test_runtime_io_sources_include_freshness_ages() -> None:
    card = _card(_config(), "runtime_io_card")
    sources = _sources(card)
    assert "runtimeSnapshot.attention_age_ms" in sources
    assert "runtimeSnapshot.gyro_age_ms" in sources


def test_game_canvas_card_declares_game_placeholder() -> None:
    card = _card(_config(), "game_canvas_card")
    widget_types = {w.get("type") for w in card.get("widgets", []) if isinstance(w, dict)}
    widget_presets = {w.get("preset") for w in card.get("widgets", []) if isinstance(w, dict)}
    assert card.get("type") == "game" or "game_placeholder" in widget_types or "game_canvas_placeholder" in widget_presets


def test_training_page_schema_and_contracts_validate() -> None:
    config = _config()
    validate_page_config(config)
    validate_action_ids(collect_action_ids_from_obj(config))
    validate_source_roots(collect_sources_from_obj(config))


def test_safe_stop_widget_is_required_danger_and_confirmed() -> None:
    card = _card(_config(), "training_control_card")
    widgets = [w for w in card.get("widgets", []) if isinstance(w, dict) and w.get("action_id") == "live.safe_stop"]
    assert widgets
    widget = widgets[0]
    assert widget.get("required") is True
    assert widget.get("variant") == "danger"
    assert "confirm" in widget or "confirmEnabled" in widget


def test_game_canvas_card_has_placeholder_contract_marker() -> None:
    card = _card(_config(), "game_canvas_card")
    contract = card.get("contract", {})
    assert contract.get("canvas_role") == "game_canvas_placeholder"
    assert contract.get("implementation_status") == "placeholder_only"
    assert contract.get("requires_legacy_fallback") is True


def test_game_hud_placeholder_fields_have_pending_contract_marker() -> None:
    card = _card(_config(), "game_hud_card")
    sources = {"gameHudJson.status", "gameHudJson.score", "gameHudJson.focus_index"}
    found = 0
    for widget in card.get("widgets", []):
        if isinstance(widget, dict) and widget.get("source") in sources:
            contract = widget.get("contract", {})
            assert contract.get("contract_status") == "pending_bridge_validation" or contract.get("prototype") is True
            found += 1
    assert found == 3
