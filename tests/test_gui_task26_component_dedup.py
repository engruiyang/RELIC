from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_game_canvas_is_lazily_created_from_one_common_card_component() -> None:
    card = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "function isGameCanvasCard" in card
    assert "Loader" in card
    assert "sourceComponent" in card
    assert "GameCanvas" in card
    assert "root.visible && root.isGameCanvasCard()" in card


def test_non_game_cards_do_not_create_hidden_game_canvas_instances() -> None:
    card = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "visible: !root.isGameCanvasCard()" in card
    assert "desktopGameCanvasLoader.active" in card
