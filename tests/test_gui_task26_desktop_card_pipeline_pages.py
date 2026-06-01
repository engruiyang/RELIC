from pathlib import Path

PAGES = [
    "HomePage.qml",
    "TrainingPage.qml",
    "UserPage.qml",
    "CalibrationPage.qml",
    "ReportPage.qml",
    "DiagnosticsPage.qml",
]


def _read_page(name: str) -> str:
    return Path("ui_qml/pages", name).read_text(encoding="utf-8")


def test_pages_expose_required_objects_to_current_card_desktop() -> None:
    for page in PAGES:
        text = _read_page(page)
        assert "property var guiBridge" in text
        assert "Page Commands" in text
        assert "Page Feedback" in text
        assert "controlStateObj" in text


def test_any_desktop_preview_bindings_do_not_add_blocked_runtime_tokens() -> None:
    for page in PAGES:
        text = _read_page(page)
        if "DesktopLayoutPreview" not in text:
            continue
        lines = text.splitlines()
        start = next(i for i, line in enumerate(lines) if "DesktopLayoutPreview" in line)
        block = "\n".join(lines[start:start + 40])
        for token in ["Repeater", "subprocess", "XMLHttpRequest"]:
            assert token not in block


def test_training_page_keeps_game_canvas_token() -> None:
    text = _read_page("TrainingPage.qml")
    assert "GameCanvas" in text
