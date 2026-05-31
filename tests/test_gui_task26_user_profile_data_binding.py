from pathlib import Path
import json
import re


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_user_credentials_card_explains_register_and_login_fields() -> None:
    data = json.loads(_read("assets/layouts/task26_examples/user_page.desktop_demo.json"))
    cards = {card.get("id"): card for card in data.get("cards", [])}
    card = cards["user_credentials_card"]
    assert "Register:" in card.get("subtitle", "")
    assert "Login:" in card.get("subtitle", "")

    labels = {w.get("id"): w.get("label") for w in card.get("widgets", [])}
    assert labels["new_user_id"] == "Register ID"
    assert labels["new_display_name"] == "Display Name"
    assert labels["login_user_id"] == "Login ID"
    assert labels["register_user_btn"] == "Register New User"


def test_card_preview_renders_input_and_select_labels_next_to_controls() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert 'root.widget1Type === "input" || root.widget1Type === "select"' in text
    assert "width: parent.width * 0.36" in text
    assert "width: parent.width * 0.60" in text
    assert "text: root.widget1Label.length > 0 ? root.widget1Label : root.widget1Id" in text


def test_gui_facade_caches_user_profile_into_control_state() -> None:
    text = _read("gui/gui_facade.py")
    assert "_last_user_profile_detail" in text
    assert "_last_user_calibration_detail" in text
    assert "def _remember_user_profile_context" in text
    assert "_remember_user_profile_context(user_id, detail, cs)" in text
    assert "_remember_user_profile_context(uid, detail, calibration)" in text
    assert 'current_user_id = merged_detail.get("current_user_id"' in text


def test_user_profile_sources_use_control_state_profile_cache() -> None:
    data = json.loads(_read("assets/layouts/task26_examples/user_page.desktop_demo.json"))
    sources = {
        w.get("id"): w.get("source")
        for card in data.get("cards", [])
        for w in card.get("widgets", [])
    }
    assert sources["profile_loaded"] == "controlStateJson.profile_loaded"
    assert sources["last_calibration"] == "controlStateJson.last_calibration_id"
    assert sources["attention_low"] == "controlStateJson.attention_low_threshold"
    assert sources["attention_high"] == "controlStateJson.attention_high_threshold"
