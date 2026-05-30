from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


PAGE_EXPECTATIONS = {
    "UserPage.qml": [
        "TASK26 User Desktop Pilot",
        "DesktopLayoutPreview",
        "task26UserLayoutPayload",
        "task26_user_layout_payload",
        "task26DesktopPilotEnabled",
        "task26LegacyFallbackVisible",
    ],
    "CalibrationPage.qml": [
        "TASK26 Calibration Desktop Pilot",
        "DesktopLayoutPreview",
        "task26CalibrationLayoutPayload",
        "task26_calibration_layout_payload",
        "task26DesktopPilotEnabled",
        "task26LegacyFallbackVisible",
    ],
    "ReportPage.qml": [
        "TASK26 Report Desktop Pilot",
        "DesktopLayoutPreview",
        "task26ReportLayoutPayload",
        "task26_report_layout_payload",
        "task26DesktopPilotEnabled",
        "task26LegacyFallbackVisible",
    ],
    "DiagnosticsPage.qml": [
        "TASK26 Diagnostics Desktop Pilot",
        "DesktopLayoutPreview",
        "task26DiagnosticsLayoutPayload",
        "task26_diagnostics_layout_payload",
        "task26DesktopPilotEnabled",
        "task26LegacyFallbackVisible",
    ],
}


def test_multi_page_desktop_pilot_tokens_present() -> None:
    for filename, tokens in PAGE_EXPECTATIONS.items():
        text = _read(f"ui_qml/pages/{filename}")
        for token in tokens:
            assert token in text, f"{filename} missing {token}"


def test_multi_page_desktop_pilot_uses_full_area_overlay() -> None:
    for filename in PAGE_EXPECTATIONS:
        text = _read(f"ui_qml/pages/{filename}")
        assert "anchors.fill: parent" in text
        assert "anchors.margins: 6" in text
        assert "z: 100" in text


def test_multi_page_legacy_tokens_are_preserved() -> None:
    checks = {
        "UserPage.qml": ["User / Profile", "User Page Actions", "Page Commands"],
        "CalibrationPage.qml": ["Calibration Page", "Calibration Status", "Page Commands"],
        "ReportPage.qml": ["Report Page", "List Sessions", "Latest Report"],
        "DiagnosticsPage.qml": ["Developer Diagnostics Console", "Live Input", "Quality / Focus"],
    }
    for filename, tokens in checks.items():
        text = _read(f"ui_qml/pages/{filename}")
        for token in tokens:
            assert token in text, f"{filename} missing legacy token {token}"


def test_multi_page_desktop_pilot_avoids_new_dynamic_components() -> None:
    for filename in PAGE_EXPECTATIONS:
        text = _read(f"ui_qml/pages/{filename}")
        for token in ["Loader", "Repeater", "subprocess", "XMLHttpRequest"]:
            assert token not in text, f"{filename} contains banned token {token}"
