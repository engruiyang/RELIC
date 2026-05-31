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


def test_report_desktop_demo_has_no_manual_or_duplicate_show_selected() -> None:
    data = json.loads(Path("assets/layouts/task26_examples/report_page.desktop_demo.json").read_text(encoding="utf-8"))
    report_widgets = [w for card in data["cards"] for w in card.get("widgets", [])]
    labels = [str(w.get("label", "")) for w in report_widgets]
    ids = [str(w.get("id", "")) for w in report_widgets]
    joined = json.dumps(data, ensure_ascii=False).lower()
    assert "show manual" not in joined
    assert "open_path_manual" not in joined
    assert "manual id" not in joined
    assert labels.count("Show Selected") == 1
    assert labels.count("Refresh Report List") == 1
    assert "List Reports" not in labels
    assert "show_selected_report" in ids
    assert "list_reports_action" not in ids


def test_report_desktop_demo_uses_formal_three_column_ratio() -> None:
    data = json.loads(Path("assets/layouts/task26_examples/report_page.desktop_demo.json").read_text(encoding="utf-8"))
    cards = {card["id"]: card for card in data["cards"]}
    assert cards["report_query_card"]["position"] == {"col": 1, "row": 1, "col_span": 4, "row_span": 8}
    assert cards["report_detail_card"]["position"] == {"col": 5, "row": 1, "col_span": 5, "row_span": 8}
    assert cards["report_actions_card"]["position"]["col_span"] == 3
    assert cards["report_popup_card"]["position"]["col_span"] == 3


def test_report_context_exposes_preview_and_paths() -> None:
    resources = GuiFacade(mode="mock").get_render_resources()
    context = resources.get("task26_report_context")
    assert isinstance(context, dict)
    for key in ["report_selected_report_path", "report_export_path", "report_preview", "report_selected_report_preview", "report_list_text"]:
        assert key in context
