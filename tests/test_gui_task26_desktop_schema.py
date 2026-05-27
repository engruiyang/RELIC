from __future__ import annotations

import json
from pathlib import Path

import pytest

from gui.desktop_coverage import validate_action_ids
from gui.desktop_schema import (
    collect_action_ids_from_obj,
    iter_task26_example_json,
    load_json,
    reject_script_like_values,
    validate_desktop_config,
    validate_page_config,
)

ROOT = Path(".")
EXAMPLES = ROOT / "assets" / "layouts" / "task26_examples"


def test_task26_examples_all_json_parse() -> None:
    files = iter_task26_example_json(ROOT)
    assert files
    for p in files:
        with p.open("r", encoding="utf-8") as f:
            json.load(f)


def test_task26_examples_reject_script_like_values_pass() -> None:
    for p in iter_task26_example_json(ROOT):
        with p.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        reject_script_like_values(obj)


def test_desktop_example_validate_pass() -> None:
    desktop = load_json(EXAMPLES / "desktop.example.json")
    validate_desktop_config(desktop)


def test_home_and_training_page_validate_pass() -> None:
    validate_page_config(load_json(EXAMPLES / "home_page.desktop_demo.json"))
    validate_page_config(load_json(EXAMPLES / "training_page.desktop_demo.json"))


def test_collect_action_ids_contains_expected() -> None:
    actions = set()
    for rel in ["desktop.example.json", "home_page.desktop_demo.json", "training_page.desktop_demo.json"]:
        actions |= collect_action_ids_from_obj(load_json(EXAMPLES / rel))
    assert "app.refresh_now" in actions
    assert "session.start" in actions
    assert "session.stop" in actions
    assert "live.safe_stop" in actions


def test_validate_action_ids_accepts_registry_plus_native() -> None:
    validate_action_ids({"app.refresh_now", "session.start", "live.safe_stop"})


def test_validate_action_ids_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        validate_action_ids({"unknown.fake_action"})
