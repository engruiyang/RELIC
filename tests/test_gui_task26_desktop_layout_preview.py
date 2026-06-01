from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_developer_lab_is_focused_console_without_legacy_layout_previews() -> None:
    text = _read("ui_qml/pages/DeveloperLabPage.qml")
    assert "Developer Lab" in text
    assert "Page Commands" in text
    assert "Page Feedback" in text
    assert "TASK26 Home Desktop Layout Preview" not in text


def test_layout_preview_qml_avoids_unsafe_runtime_tokens() -> None:
    for path in [Path("ui_qml/components/DesktopLayoutCardPreview.qml"), Path("ui_qml/components/DesktopLayoutPreview.qml")]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in ["subprocess", "Popen", "os.system", "XMLHttpRequest"]:
            assert token not in text
