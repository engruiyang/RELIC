from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_home_and_training_pages_use_current_desktop_card_pilot_tokens() -> None:
    home = _read("ui_qml/pages/HomePage.qml")
    training = _read("ui_qml/pages/TrainingPage.qml")
    assert "Page Commands" in home and "Page Feedback" in home
    assert "GameCanvas" in training
    assert "Page Commands" in training and "Page Feedback" in training


def test_new_desktop_style_qml_avoids_unsafe_runtime_tokens() -> None:
    for path in [Path("ui_qml/components/DesktopLayoutCardPreview.qml"), Path("ui_qml/pages/HomePage.qml"), Path("ui_qml/pages/TrainingPage.qml")]:
        text = path.read_text(encoding="utf-8")
        for token in ["subprocess", "Popen", "os.system", "XMLHttpRequest"]:
            assert token not in text
