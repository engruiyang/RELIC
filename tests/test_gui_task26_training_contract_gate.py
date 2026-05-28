from __future__ import annotations

import subprocess
from pathlib import Path

from gui.desktop_coverage import validate_action_ids
from gui.desktop_model import build_training_card_slots, build_training_contract_summary
from gui.desktop_schema import (
    collect_action_ids_from_obj,
    collect_sources_from_obj,
    load_json,
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


def test_training_contract_doc_exists() -> None:
    assert (ROOT / "docs" / "gui" / "TASK26F_training_contract.md").exists()


def test_training_config_contracts_validate() -> None:
    config = load_json(CONFIG_PATH)
    validate_page_config(config)
    validate_action_ids(collect_action_ids_from_obj(config))
    validate_source_roots(collect_sources_from_obj(config))


def test_training_contract_summary_shape_and_guards() -> None:
    summary = build_training_contract_summary(ROOT)
    assert summary["page_id"] == "training"
    assert summary["safe_stop_present"] is True
    assert REQUIRED_CARDS <= set(summary["required_card_ids"])
    assert "gameHudJson.status" in summary["placeholder_sources"] or "gameHudJson.score" in summary["placeholder_sources"]
    assert "placeholder" in summary["game_canvas_card_status"]
    assert summary["training_slots_supported"] is True
    assert summary["training_injection_supported"] is True


def test_training_slots_are_supported_in_task26f2_cli() -> None:
    result = subprocess.run(
        ["python", "tools/build_task26_render_model.py", "--page", "training", "--slots"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "training_desktop_render_model_slots.example.json" in result.stdout
    slots = build_training_card_slots(ROOT)
    assert len(slots) == 7


def test_training_injection_is_supported_in_task26f2_cli() -> None:
    result = subprocess.run(
        ["python", "tools/build_task26_render_model.py", "--page", "training", "--slots", "--injection"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "training_desktop_render_model_slots_injection.example.json" in result.stdout


def test_task26_contract_gate_strict_includes_training() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py", "--strict"], check=True, capture_output=True, text=True)
    assert "TASK26 contracts strict ok" in result.stdout
