from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gui.desktop_model import build_home_render_model, build_home_render_model_summary, build_page_render_model, build_render_model_summary, write_render_model

EXAMPLES = Path("assets/layouts/task26_examples")


def _home_cfg() -> dict:
    return json.loads((EXAMPLES / "home_page.desktop_demo.json").read_text(encoding="utf-8"))


def test_build_page_render_model_home() -> None:
    model = build_page_render_model(_home_cfg())
    assert model["page_id"] == "home"
    assert model["cards"]


def test_runtime_and_quick_cards_exist() -> None:
    model = build_page_render_model(_home_cfg())
    cards = {c["id"]: c for c in model["cards"]}
    assert "runtime_io_card" in cards
    assert "quick_actions_card" in cards


def test_all_cards_have_xywh_positive() -> None:
    model = build_page_render_model(_home_cfg())
    for c in model["cards"]:
        for key in ["x", "y", "width", "height"]:
            assert isinstance(c[key], (int, float))
        assert c["width"] > 0
        assert c["height"] > 0


def test_runtime_io_card_locked_true() -> None:
    model = build_page_render_model(_home_cfg())
    cards = {c["id"]: c for c in model["cards"]}
    assert cards["runtime_io_card"]["locked"] is True


def test_live_safe_stop_in_render_model() -> None:
    model = build_page_render_model(_home_cfg())
    text = json.dumps(model, ensure_ascii=False)
    assert "live.safe_stop" in text


def test_non_grid_layout_raises() -> None:
    cfg = _home_cfg()
    cfg["layout"]["mode"] = "absolute"
    with pytest.raises(ValueError):
        build_page_render_model(cfg)


def test_card_out_of_grid_raises() -> None:
    cfg = _home_cfg()
    cfg["cards"][0]["position"]["col"] = 99
    with pytest.raises(ValueError):
        build_page_render_model(cfg)


def test_button_action_id_non_string_raises() -> None:
    cfg = _home_cfg()
    target = None
    for c in cfg["cards"]:
        if c.get("id") == "quick_actions_card":
            target = c
            break
    assert target is not None
    target["widgets"][0]["action_id"] = 123
    with pytest.raises(ValueError):
        build_page_render_model(cfg)


def test_write_render_model_writes_readable_json(tmp_path: Path) -> None:
    model = build_page_render_model(_home_cfg())
    out = tmp_path / "out.json"
    write_render_model(model, out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["page_id"] == "home"


def test_build_home_render_model() -> None:
    model = build_home_render_model(Path("."))
    assert model["page_id"] == "home"


def test_generated_render_model_has_no_script_tokens(tmp_path: Path) -> None:
    model = build_page_render_model(_home_cfg())
    out = tmp_path / "home_desktop_render_model.example.json"
    write_render_model(model, out)
    text = out.read_text(encoding="utf-8").lower()
    for token in ["function", "eval", "script", "javascript:", "=>", "onclicked", "qt.calllater"]:
        assert token not in text


def test_build_render_model_summary_basic() -> None:
    model = build_page_render_model(_home_cfg())
    summary = build_render_model_summary(model)
    assert summary["page_id"] == "home"
    assert summary["card_count"] == len(model["cards"])
    assert summary["widget_count"] > 0
    assert summary["preview_lines"]


def test_build_home_render_model_summary_has_expected_cards() -> None:
    summary = build_home_render_model_summary(Path("."))
    assert "runtime_io_card" in summary["card_ids"]
    assert "quick_actions_card" in summary["card_ids"]


def test_summary_has_no_script_like_tokens() -> None:
    summary = build_home_render_model_summary(Path("."))
    text = json.dumps(summary, ensure_ascii=False).lower()
    for token in ["function", "eval", "script", "javascript:", "=>", "onclicked", "qt.calllater"]:
        assert token not in text
