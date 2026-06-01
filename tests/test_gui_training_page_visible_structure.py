from pathlib import Path
import re


def test_training_page_readiness_tokens() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    for token in [
        "Training Readiness",
        "formal_training_allowed",
        "readiness_reason",
        "Start Session",
        "Stop Session",
        "Session Status",
        "Game Status",
        "Runtime Signal Summary",
        "Game HUD Summary",
        "GameCanvas will be restored in TASK24",
        "Page Commands",
        "Page Feedback",
        "user.show_profile",
        "calibration.status",
        "session.start",
        "session.stop",
        "session.status",
        "game.status",
    ]:
        assert token in text


def test_training_page_uses_existing_native_actions_without_forbidden_patterns() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    assert "GameCanvas {" in text
    assert "Loader {" in text  # game canvas is lazily loaded to avoid hidden-instance lag
    for forbidden in ["Repeater", "subprocess", "Popen", "os.system", "background: Rectangle"]:
        assert forbidden not in text
    assert re.search(r"\binterval\s*:\s*100\b(?!\s*0)", text) is None
