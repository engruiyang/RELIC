from pathlib import Path


def _text() -> str:
    return Path("ui_qml/pages/CalibrationPage.qml").read_text(encoding="utf-8")


def test_calibration_page_visible_structure_tokens() -> None:
    text = _text()
    for token in [
        "Calibration requires a current user.",
        "No current user loaded.",
        "Current User Gate",
        "Current User Calibration",
        "Calibration Status",
        "List Calibrations",
        "Latest Calibration",
        "Show Calibration",
        "Bind Calibration",
        "Calibration History",
        "selected_calibration_id",
        "Show Selected Calibration",
        "Bind Selected Calibration",
        "Calibration Detail",
        "Calibration Action Result",
        "No calibration records.",
        "Calibration Progress",
        "Start IPC Calibration",
        "Refresh Calibration Progress",
        "Full phase prompts",
        "Full Calibration Detail",
        "Page Commands",
        "Page Feedback",
    ]:
        assert token in text


def test_calibration_page_uses_native_actions_without_forbidden_patterns() -> None:
    text = _text()
    for action in [
        "calibration.status",
        "calibration.list",
        "calibration.latest",
        "calibration.show",
        "calibration.bind",
        "calibration.cancel",
        "calibration.start",
    ]:
        assert action in text
    for forbidden in ["Loader", "Repeater", "subprocess", "Popen", "os.system", "interval: 100", "GameCanvas {"]:
        assert forbidden not in text
