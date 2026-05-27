from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from gui.desktop_coverage import (
    collect_cards_fields_buttons_from_pages,
    load_pipeline_bindings,
    validate_pipeline_coverage,
    validate_safe_stop_accessible,
)
from gui.desktop_schema import load_json

EXAMPLES = Path("assets/layouts/task26_examples")


def _inventory() -> dict[str, set[str]]:
    desktop = load_json(EXAMPLES / "desktop.example.json")
    home = load_json(EXAMPLES / "home_page.desktop_demo.json")
    training = load_json(EXAMPLES / "training_page.desktop_demo.json")
    return collect_cards_fields_buttons_from_pages([home, training], desktop)


def test_pipeline_bindings_loadable() -> None:
    items = load_pipeline_bindings(EXAMPLES / "pipeline_ui_bindings.example.json")
    assert items


def test_inventory_collect_cards_fields_buttons() -> None:
    inv = _inventory()
    assert "runtime_io_card" in inv["cards"]
    assert "runtimeSnapshot.stream_alive" in inv["fields"]
    assert "app.refresh_now" in inv["buttons"]


def test_inventory_buttons_contains_live_safe_stop() -> None:
    inv = _inventory()
    assert "live.safe_stop" in inv["buttons"]


def test_validate_safe_stop_accessible_pass() -> None:
    validate_safe_stop_accessible(_inventory())


def test_validate_pipeline_coverage_non_strict_pass_on_examples() -> None:
    bindings = load_pipeline_bindings(EXAMPLES / "pipeline_ui_bindings.example.json")
    validate_pipeline_coverage(bindings, _inventory(), strict=False)


def test_validate_pipeline_coverage_strict_pass_on_examples() -> None:
    bindings = load_pipeline_bindings(EXAMPLES / "pipeline_ui_bindings.example.json")
    validate_pipeline_coverage(bindings, _inventory(), strict=True)


def test_validate_safe_stop_accessible_fail_when_missing() -> None:
    inv = _inventory()
    inv["buttons"] = set(inv["buttons"]) - {"live.safe_stop"}
    with pytest.raises(ValueError):
        validate_safe_stop_accessible(inv)


def test_validate_pipeline_coverage_strict_fail_when_missing_card() -> None:
    bindings = load_pipeline_bindings(EXAMPLES / "pipeline_ui_bindings.example.json")
    inv = _inventory()
    inv["cards"] = set(inv["cards"]) - {"runtime_io_card"}
    with pytest.raises(ValueError):
        validate_pipeline_coverage(bindings, inv, strict=True)


def test_validate_pipeline_coverage_strict_fail_when_missing_field() -> None:
    bindings = load_pipeline_bindings(EXAMPLES / "pipeline_ui_bindings.example.json")
    inv = _inventory()
    inv["fields"] = set(inv["fields"]) - {"runtimeSnapshot.stream_alive"}
    with pytest.raises(ValueError):
        validate_pipeline_coverage(bindings, inv, strict=True)


def test_validate_pipeline_coverage_strict_fail_when_missing_button() -> None:
    bindings = load_pipeline_bindings(EXAMPLES / "pipeline_ui_bindings.example.json")
    inv = _inventory()
    inv["buttons"] = set(inv["buttons"]) - {"app.refresh_now"}
    with pytest.raises(ValueError):
        validate_pipeline_coverage(bindings, inv, strict=True)


def test_cli_strict_mode_passes() -> None:
    result = subprocess.run(["python", "tools/check_gui_pipeline_coverage.py", "--strict"], check=True, capture_output=True, text=True)
    assert "TASK26 pipeline coverage strict ok" in result.stdout
