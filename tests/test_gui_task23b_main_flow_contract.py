from __future__ import annotations

from pathlib import Path


PAGES = {
    "ui_qml/pages/UserPage.qml": [
        "User / Profile",
        "Current User Summary",
        "User List",
        "Switch User",
        "Profile Detail Popup",
        "missing_input",
    ],
    "ui_qml/pages/CalibrationPage.qml": [
        "Calibration requires a current user",
        "Current User Calibration",
        "Calibration History",
        "Calibration Progress",
        "Start IPC Calibration",
        "selected_calibration_id",
        "Full Calibration Detail",
    ],
    "ui_qml/pages/TrainingPage.qml": [
        "Training Readiness",
        "formal_training_allowed",
        "readiness_reason",
        "Start Session",
        "Stop Session",
        "GameCanvas will be restored in TASK24",
    ],
    "ui_qml/pages/ReportPage.qml": [
        "Report Readiness",
        "Latest Report",
        "Session List",
        "Session Detail",
        "selected_session_id",
        "missing_session_id",
        "Report Action Result",
    ],
}


BANNED_TOKENS = [
    "GameCanvas {",
    "Loader",
    "Repeater",
    "interval: 100",
    "subprocess",
    "Popen",
    "os.system",
]


REQUIRED_ACTIONS = [
    "user.list",
    "user.create",
    "user.load",
    "user.load_current",
    "user.show_profile",
    "calibration.status",
    "calibration.list",
    "calibration.latest",
    "calibration.show",
    "calibration.bind",
    "calibration.start",
    "calibration.poll",
    "session.start",
    "session.stop",
    "session.status",
    "game.status",
    "report.refresh",
    "report.list",
    "report.show",
    "report.export",
]


def test_task23b_page_tokens_present() -> None:
    for page, tokens in PAGES.items():
        text = Path(page).read_text(encoding="utf-8")
        for token in tokens:
            assert token in text, f"missing token {token!r} in {page}"


def test_qml_banned_tokens_absent() -> None:
    for qml in Path("ui_qml").rglob("*.qml"):
        if qml.name == "GameCanvas.qml":
            continue
        text = qml.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text, f"banned token {token!r} found in {qml}"


def test_gui_facade_required_actions_declared() -> None:
    facade_text = Path("gui/gui_facade.py").read_text(encoding="utf-8")
    for action in REQUIRED_ACTIONS:
        assert action in facade_text, f"required action {action!r} missing in gui_facade.py"
