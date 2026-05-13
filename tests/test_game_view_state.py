from __future__ import annotations

import json

import pytest

from game.game_view_state import GameViewState, GameViewStateValidationError


def _valid_dict() -> dict:
    return {
        "schema_version": "game_view.v1",
        "session_id": "s1",
        "game_id": "fake_game",
        "view_type": "fake_status",
        "updated_at_ms": 123,
        "status": "running",
        "score": 10.0,
        "combo": 2,
        "level": 1,
        "control_state": "STABLE_FOCUS",
        "quality_state": "ok",
        "feedback_hint": "stable",
        "hud": {"fi": 72.0},
        "entities": [{"id": "target_1", "type": "target"}],
        "effects": [{"type": "highlight", "target_id": "target_1"}],
        "layout_hints": {"preferred_aspect": "16:9"},
    }


def test_to_dict_and_json_serializable() -> None:
    v = GameViewState.from_dict(_valid_dict())
    d = v.to_dict()
    json.dumps(d)


def test_from_dict_missing_required_field_fails() -> None:
    d = _valid_dict(); d.pop("session_id")
    with pytest.raises(GameViewStateValidationError):
        GameViewState.from_dict(d)


def test_invalid_types_fail() -> None:
    d = _valid_dict(); d["entities"] = {"bad": 1}
    with pytest.raises(GameViewStateValidationError):
        GameViewState.from_dict(d)


def test_non_serializable_fail() -> None:
    d = _valid_dict(); d["hud"] = {"x": object()}
    with pytest.raises(GameViewStateValidationError):
        GameViewState.from_dict(d)
