from __future__ import annotations

from pathlib import Path
import subprocess

from gui.desktop_model import (
    diff_home_slot_injection_contract,
    expected_home_slot_qml_properties,
    snake_to_qml_camel,
)


def test_contract_gate_tool_exists() -> None:
    assert Path("tools/check_task26_contracts.py").exists()


def test_contract_gate_default_passes() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py"], check=True, capture_output=True, text=True)
    assert "TASK26 contracts ok" in result.stdout


def test_contract_gate_strict_passes() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py", "--strict"], check=True, capture_output=True, text=True)
    assert "TASK26 contracts strict ok" in result.stdout


def test_contract_gate_strict_show_diff_passes() -> None:
    result = subprocess.run(
        ["python", "tools/check_task26_contracts.py", "--strict", "--show-diff"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "TASK26 injection contract diff" in result.stdout


def test_snake_to_qml_camel_mapping() -> None:
    assert snake_to_qml_camel("slot1_card_id") == "slot1CardId"
    assert snake_to_qml_camel("slot1_action_ids_text") == "slot1ActionIdsText"
    assert snake_to_qml_camel("slot_count") == "slotCount"


def test_expected_home_slot_qml_properties_contains_required() -> None:
    fields = expected_home_slot_qml_properties()
    assert "slot1CardId" in fields
    assert "slot4FirstWidgetLabelsText" in fields


def test_diff_reports_missing_in_qml() -> None:
    payload_fields = {"slot1_card_id", "slot_count"}
    qml_properties = {"slotCount"}
    developer_lab_properties = {"slotCount", "slot1CardId"}
    diff = diff_home_slot_injection_contract(payload_fields, qml_properties, developer_lab_properties)
    assert "slot1CardId" in diff["missing_in_qml"]


def test_diff_reports_missing_in_developer_lab() -> None:
    payload_fields = {"slot1_card_id", "slot_count"}
    qml_properties = {"slotCount", "slot1CardId"}
    developer_lab_properties = {"slotCount"}
    diff = diff_home_slot_injection_contract(payload_fields, qml_properties, developer_lab_properties)
    assert "slot1CardId" in diff["missing_in_developer_lab"]
