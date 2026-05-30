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


def test_pages_pass_required_objects_to_desktop_layout_preview() -> None:
    expectations = {
        "HomePage.qml": ["guiBridge:", "runtimeSnapshotObj:"],
        "TrainingPage.qml": ["guiBridge:", "runtimeSnapshotObj:", "sessionStateObj:", "gameHudObj:"],
        "UserPage.qml": ["guiBridge:", "controlStateObj:"],
        "CalibrationPage.qml": ["guiBridge:", "controlStateObj:"],
        "ReportPage.qml": ["guiBridge:"],
        "DiagnosticsPage.qml": ["guiBridge:", "runtimeSnapshotObj:"],
    }
    for page, tokens in expectations.items():
        text = _read_page(page)
        assert "DesktopLayoutPreview" in text
        for token in tokens:
            assert token in text


def test_pages_keep_task26_pilot_and_legacy_fallback_tokens() -> None:
    for page in PAGES:
        text = _read_page(page)
        assert "task26DesktopPilotEnabled" in text
        assert "task26LegacyFallbackVisible" in text


def test_desktop_preview_page_bindings_do_not_add_blocked_dynamic_qml_tokens() -> None:
    for page in PAGES:
        lines = _read_page(page).splitlines()
        start = next(i for i, line in enumerate(lines) if "DesktopLayoutPreview" in line)
        block = "\n".join(lines[start:start + 24])
        for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest"]:
            assert token not in block


def test_training_page_keeps_game_canvas_fallback_token() -> None:
    text = _read_page("TrainingPage.qml")
    assert "GameCanvas" in text
