from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from gui.desktop_model import (
    build_task26_fixed_card_registry,
    build_task26_fixed_card_registry_from_configs,
    build_task26_fixed_card_render_resource,
    validate_task26_fixed_card_policy,
    validate_task26_page_fixed_card_policy,
)
from gui.gui_facade import GuiFacade

ROOT = Path(".")
EXAMPLE_ROOT = Path("assets/layouts/task26_examples")


def _load_json(name: str) -> dict:
    with (EXAMPLE_ROOT / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _card(page: dict, card_id: str) -> dict:
    return next(c for c in page["cards"] if c["id"] == card_id)


def test_fixed_card_registry_covers_all_task26_pages() -> None:
    registry = build_task26_fixed_card_registry(ROOT)
    assert registry["version"] == "task26.fixed_cards.v1"
    assert set(registry["pages"]) == {"home", "training", "user", "calibration", "report", "diagnostics"}
    assert registry["fixed_card_count"] >= 1
    assert registry["optional_card_count"] >= 1

    for page_id, page in registry["pages"].items():
        assert page["fixed_card_ids"], page_id
        for card in page["cards"]:
            if card["fixed"]:
                assert card["required"] is True
                assert card["locked"] is True
                assert card["allow_remove"] is False
            else:
                assert card["required"] is False
                assert card["locked"] is False
                assert card["allow_remove"] is True


def test_fixed_card_policy_accepts_current_examples() -> None:
    validate_task26_fixed_card_policy(ROOT)


@pytest.mark.parametrize(
    "json_name,card_id",
    [
        ("home_page.desktop_demo.json", "runtime_io_card"),
        ("training_page.desktop_demo.json", "training_control_card"),
        ("user_page.desktop_demo.json", "user_current_card"),
        ("calibration_page.desktop_demo.json", "calibration_status_card"),
        ("report_page.desktop_demo.json", "report_actions_card"),
        ("diagnostics_page.desktop_demo.json", "runtime_io_card"),
    ],
)
def test_fixed_cards_cannot_be_marked_removable(json_name: str, card_id: str) -> None:
    page = _load_json(json_name)
    edited = copy.deepcopy(page)
    _card(edited, card_id)["card_policy"]["allow_remove"] = True
    with pytest.raises(ValueError, match="fixed card cannot allow_remove"):
        validate_task26_page_fixed_card_policy(edited)


def test_optional_cards_must_remain_removable() -> None:
    page = _load_json("home_page.desktop_demo.json")
    edited = copy.deepcopy(page)
    optional = _card(edited, "recent_session_card")
    optional["card_policy"]["allow_remove"] = False
    with pytest.raises(ValueError, match="optional card must allow_remove"):
        validate_task26_page_fixed_card_policy(edited)


def test_required_widget_forces_parent_card_to_be_fixed() -> None:
    page = _load_json("home_page.desktop_demo.json")
    edited = copy.deepcopy(page)
    optional = _card(edited, "recent_session_card")
    optional["widgets"][0]["required"] = True
    with pytest.raises(ValueError, match="fixed card must have required=true"):
        validate_task26_page_fixed_card_policy(edited)


def test_fixed_card_render_resource_and_facade_expose_registry() -> None:
    resource = build_task26_fixed_card_render_resource(ROOT)
    assert resource["task26_fixed_card_status"] == "ok"
    registry = resource["task26_fixed_card_registry"]
    assert "home" in registry["pages"]
    assert "runtime_io_card" in registry["pages"]["home"]["fixed_card_ids"]

    resources = GuiFacade(mode="mock").get_render_resources()
    assert resources["task26_fixed_card_status"] == "ok"
    assert "training" in resources["task26_fixed_card_registry"]["pages"]


def test_fixed_card_registry_from_configs_rejects_duplicate_card_ids() -> None:
    page = _load_json("home_page.desktop_demo.json")
    edited = copy.deepcopy(page)
    duplicated = copy.deepcopy(edited["cards"][0])
    edited["cards"].append(duplicated)
    with pytest.raises(ValueError, match="duplicate card id"):
        build_task26_fixed_card_registry_from_configs([edited])


def test_task26_contract_gate_runs_fixed_card_policy() -> None:
    result = subprocess.run(
        [sys.executable, "tools/check_task26_contracts.py", "--strict"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "TASK26 contracts strict ok" in result.stdout
