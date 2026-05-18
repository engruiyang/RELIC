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
        "TraceLock Difficulty",
        "Difficulty Control",
        "Apply Difficulty",
        "Reset Auto Difficulty",
        "difficultyStartPayload",
        "session.start will sync difficulty",
        "Button feedback is text-based",
        "difficulty_button_state",
        "last difficulty button",
        "Apply Difficulty pressed visually",
        "Reset Auto Difficulty pressed visually",
        "sent_via_legacy_command",
        "difficulty_mode",
        "debug_difficulty",
        "dynamic_difficulty_enabled",
        "effective_level",
        "game_duration_ms",
        "time_left_ms",
        "game_completed",
        "target_pressure_level",
        "game.difficulty",
        "Design Pack Status",
        "design_pack",
        "game_styles",
        "effect_styles",
        "TASK25 design_pack game_styles active",
        "designThemeObj",
        "gameStyleObj",
        "effectStyleObj",
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
    assert "GameCanvas {" in text
    for forbidden in ["Loader", "Repeater", "interval: 100", "subprocess", "Popen", "os.system", "background: Rectangle"]:
        assert forbidden not in text
