from pathlib import Path


def test_training_page_apply_difficulty_respects_selected_mode() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    start = text.index("    function applyTraceLockDifficulty()")
    end = text.index("    function resetTraceLockAutoDifficulty()", start)
    block = text[start:end]

    assert 'selectedDifficultyMode = "manual"' not in block
    assert 'dispatchDifficulty("manual", selectedDifficultyLevel' not in block
    assert 'var mode = selectedDifficultyMode === "auto" ? "auto" : "manual"' in block
    assert 'dispatchDifficulty(mode, level, label)' in block


def test_training_page_reset_auto_still_dispatches_auto() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    start = text.index("    function resetTraceLockAutoDifficulty()")
    end = text.index("    function difficultyValue", start)
    block = text[start:end]

    assert 'selectedDifficultyMode = "auto"' in block
    assert 'dispatchDifficulty("auto", null, "Reset Auto Difficulty")' in block
