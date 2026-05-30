import json
from pathlib import Path

from gui.desktop_model import (
    build_task26_page_layout_preview_payload,
    validate_desktop_layout_preview_payload,
)
from gui.gui_facade import GuiFacade


def test_multi_page_desktop_demo_json_files_exist_and_parse() -> None:
    for page_id in ["user", "calibration", "report", "diagnostics"]:
        path = Path(f"assets/layouts/task26_examples/{page_id}_page.desktop_demo.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["page_id"] == page_id
        assert data["cards"]


def test_multi_page_layout_preview_payloads_are_valid() -> None:
    for page_id in ["user", "calibration", "report", "diagnostics"]:
        payload = build_task26_page_layout_preview_payload(Path("."), page_id)
        assert payload["page_id"] == page_id
        assert payload["card_count"] >= 3
        validate_desktop_layout_preview_payload(payload, max_cards=7)


def test_facade_exposes_multi_page_layout_resources() -> None:
    resources = GuiFacade(mode="mock").get_render_resources()
    for page_id in ["user", "calibration", "report", "diagnostics"]:
        prefix = f"task26_{page_id}_layout"
        assert resources[f"{prefix}_status"] == "ok"
        payload = resources[f"{prefix}_payload"]
        assert payload["page_id"] == page_id
        validate_desktop_layout_preview_payload(payload, max_cards=7)


def test_contract_gate_includes_multi_page_examples() -> None:
    import subprocess

    default = subprocess.run(["python", "tools/check_task26_contracts.py"], check=True, capture_output=True, text=True)
    strict = subprocess.run(["python", "tools/check_task26_contracts.py", "--strict"], check=True, capture_output=True, text=True)
    assert "TASK26 contracts ok" in default.stdout
    assert "TASK26 contracts strict ok" in strict.stdout
