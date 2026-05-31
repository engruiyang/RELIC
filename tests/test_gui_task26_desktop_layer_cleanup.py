from pathlib import Path


PAGES = {
    "HomePage.qml": "root",
    "TrainingPage.qml": "trainingPage",
    "UserPage.qml": "root",
    "CalibrationPage.qml": "root",
    "ReportPage.qml": "reportPage",
    "DiagnosticsPage.qml": "root",
}


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_desktop_overlays_are_enabled_only_when_desktop_pilot_is_enabled() -> None:
    for page, root_id in PAGES.items():
        text = _read(f"ui_qml/pages/{page}")
        assert "DesktopLayoutPreview" in text
        assert "z: 100" in text
        assert f"visible: {root_id}.task26DesktopPilotEnabled" in text
        assert f"enabled: {root_id}.task26DesktopPilotEnabled" in text


def test_legacy_layers_are_disabled_by_default() -> None:
    for page, root_id in PAGES.items():
        text = _read(f"ui_qml/pages/{page}")
        assert "property bool task26LegacyFallbackVisible: false" in text
        assert f"visible: {root_id}.task26LegacyFallbackVisible" in text
        assert f"enabled: {root_id}.task26LegacyFallbackVisible" in text


def test_desktop_button_signal_handlers_use_formal_parameters() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "onActionRequested: root.invokeDesktopAction(actionId)" not in text
    assert "onActionRequested: function(actionId)" in text


def test_pages_keep_legacy_fallback_tokens() -> None:
    checks = {
        "HomePage.qml": ["State Summary", "Action Panel"],
        "TrainingPage.qml": ["Training Page", "GameCanvas will be restored in TASK24"],
        "UserPage.qml": ["User / Profile", "Create / Load"],
        "CalibrationPage.qml": ["Calibration Page", "Current User Gate"],
        "ReportPage.qml": ["Report Page", "Report Readiness"],
        "DiagnosticsPage.qml": ["Developer Diagnostics Console", "Diagnostics Refresh"],
    }
    for page, tokens in checks.items():
        text = _read(f"ui_qml/pages/{page}")
        for token in tokens:
            assert token in text
