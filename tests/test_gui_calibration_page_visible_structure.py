from pathlib import Path
import re


def _has_exact_interval_100(text: str) -> bool:
    return re.search(r"\binterval\s*:\s*100\b(?!\s*0)", text) is not None


def test_calibration_page_visible_tokens() -> None:
    text = Path("ui_qml/pages/CalibrationPage.qml").read_text(encoding="utf-8")
    for token in [
        "Calibration",
        "calibration.start",
        "calibration.poll",
        "calibration.status",
        "calibration_progress",
        "Page Commands",
        "Page Feedback",
    ]:
        assert token in text


def test_calibration_page_uses_native_actions_without_forbidden_patterns() -> None:
    text = Path("ui_qml/pages/CalibrationPage.qml").read_text(encoding="utf-8")
    for forbidden in ["Loader", "Repeater", "subprocess", "Popen", "os.system", "GameCanvas {"]:
        assert forbidden not in text
    assert not _has_exact_interval_100(text)
    # A slower calibration poll is allowed; it is separate from the 50 ms GameCanvas path.
    assert "interval: 1000" in text
