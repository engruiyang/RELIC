from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_legacy_preview_wall_is_not_active_in_developer_lab() -> None:
    text = _read("ui_qml/pages/DeveloperLabPage.qml")
    assert "Removed legacy preview tokens intentionally" in text or "Developer Lab focused console" in text
    assert "TASK26 Desktop Card Preview" not in text


def test_game_canvas_loader_is_active_only_for_game_canvas_card() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "root.visible && root.isGameCanvasCard()" in text
    assert "visible: !root.isGameCanvasCard()" in text
