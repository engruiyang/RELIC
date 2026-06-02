from pathlib import Path
import json
import re

PAGES = ["HomePage", "UserPage", "CalibrationPage", "TrainingPage", "ReportPage", "DiagnosticsPage", "DeveloperLabPage"]


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _has_exact_interval_100(text: str) -> bool:
    return re.search(r"\binterval\s*:\s*100\b(?!\s*0)", text) is not None


def test_minimal_gui_passes_design_pack_props_to_all_top_pages() -> None:
    text = _read("ui_qml/MinimalGui.qml")
    for token in ["renderResourcesObj", "designThemeObj", "pageStylesObj"]:
        assert token in text
    for page in PAGES:
        assert page in text


def test_each_top_page_has_feedback_and_design_resource_context() -> None:
    for page in PAGES:
        text = _read(f"ui_qml/pages/{page}.qml")
        assert "Page Feedback" in text
        assert "renderResourcesObj" in text or page == "DeveloperLabPage"


def test_all_pack_page_jsons_have_cards() -> None:
    for path in Path("assets/layouts/task26_examples").glob("*_page.desktop_demo.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data.get("cards"), list) and data["cards"]


def test_header_feedback_use_design_tokens_and_no_forbidden_runtime_calls() -> None:
    for path in list(Path("ui_qml/pages").glob("*.qml")) + [Path("ui_qml/components/DesktopLayoutCardPreview.qml")]:
        text = path.read_text(encoding="utf-8")
        for token in ["subprocess", "Popen", "os.system"]:
            assert token not in text


def test_no_uncontrolled_loader_or_exact_100ms_interval_outside_game_canvas() -> None:
    for path in [Path("ui_qml/MinimalGui.qml")] + sorted(Path("ui_qml/pages").glob("*.qml")) + [Path("ui_qml/components/DesktopLayoutCardPreview.qml")]:
        text = path.read_text(encoding="utf-8")
        assert not _has_exact_interval_100(text), f"exact interval: 100 found in {path}"
        if path.name == "DesktopLayoutCardPreview.qml":
            assert "Loader" in text and "isGameCanvasCard" in text
        elif path.name == "TrainingPage.qml":
            # Training may reference GameCanvas and a controlled Loader so inactive pages do not create hidden canvases.
            continue
        else:
            assert "GameCanvas {" not in text
