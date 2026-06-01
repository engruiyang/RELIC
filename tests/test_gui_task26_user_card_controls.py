from pathlib import Path
import json


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_desktop_card_preview_supports_input_select_and_popup() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "TextField" in text
    assert "widget1Type === \"input\"" in text or "root.widget1Type === \"input\"" in text
    assert "ConfigSelectWidget" in text
    assert "popup" in text.lower() or "lastDesktopAction" in text
    # Loader is allowed only to lazily create the active GameCanvas card.
    assert "Loader" in text and "isGameCanvasCard" in text


def test_user_page_declares_profile_and_login_controls() -> None:
    data = json.loads(_read("assets/layouts/task26_examples/user_page.desktop_demo.json"))
    actions = {w.get("action_id") for c in data.get("cards", []) for w in c.get("widgets", [])}
    assert {"user.create", "user.load", "user.show_profile"} <= actions
