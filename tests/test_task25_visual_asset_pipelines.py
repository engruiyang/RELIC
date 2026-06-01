from pathlib import Path
import json


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_panel_header_feedback_asset_pipelines_are_wired() -> None:
    minimal = _read("ui_qml/MinimalGui.qml")
    assert "renderResourcesObj" in minimal
    assert "designThemeObj" in minimal
    for page in ["HomePage", "TrainingPage", "UserPage", "CalibrationPage", "ReportPage", "DiagnosticsPage"]:
        text = _read(f"ui_qml/pages/{page}.qml")
        assert "Page Feedback" in text


def test_page_layout_jsons_have_cards_for_asset_skinning() -> None:
    for path in Path("assets/layouts/task26_examples").glob("*_page.desktop_demo.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data.get("cards"), list) and data["cards"]
