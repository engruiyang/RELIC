from pathlib import Path


def test_training_page_readiness_tokens() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    for token in [
        "Training Readiness",
        "formal_training_allowed",
        "readiness_reason",
        "Refresh Readiness",
        "Start Session",
        "Stop Session",
        "Session Status",
        "Game Status",
        "Runtime Signal Summary",
        "Game HUD Summary",
        "Training Action Result",
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
    for forbidden in ["GameCanvas {", "Loader", "Repeater", "interval: 100", "subprocess", "Popen", "os.system"]:
        assert forbidden not in text
