from pathlib import Path
import json


def _read(path: str) -> str:
    return Path(path).read_text(encoding='utf-8')


def test_user_desktop_json_contains_card_form_widgets() -> None:
    data = json.loads(_read('assets/layouts/task26_examples/user_page.desktop_demo.json'))
    cards = {card['id']: card for card in data['cards']}
    assert 'user_credentials_card' in cards
    assert 'user_selector_card' in cards
    assert 'user_profile_popup_card' in cards

    credential_types = [w['type'] for w in cards['user_credentials_card']['widgets']]
    selector_types = [w['type'] for w in cards['user_selector_card']['widgets']]
    popup_types = [w['type'] for w in cards['user_profile_popup_card']['widgets']]

    assert credential_types.count('input') >= 3
    assert 'select' in selector_types
    assert 'select' in popup_types
    assert any(w.get('action_id') == 'user.create' for w in cards['user_credentials_card']['widgets'])
    assert any('${input.new_user_id}' in json.dumps(w, ensure_ascii=False) for w in cards['user_credentials_card']['widgets'])
    assert any('${select.selected_user_id}' in json.dumps(w, ensure_ascii=False) for w in cards['user_selector_card']['widgets'])


def test_desktop_model_exposes_select_options_text() -> None:
    from gui.desktop_model import build_user_layout_render_resource, validate_desktop_layout_preview_payload

    payload = build_user_layout_render_resource(Path("."))["task26_user_layout_payload"]
    validate_desktop_layout_preview_payload(payload)

    card_count = int(payload.get("card_count", 0))

    selector_index = None
    credentials_index = None
    for i in range(1, card_count + 1):
        if payload.get(f"card{i}_id") == "user_selector_card":
            selector_index = i
        if payload.get(f"card{i}_id") == "user_credentials_card":
            credentials_index = i

    assert selector_index is not None
    assert payload[f"card{selector_index}_widget1_type"] == "select"
    assert "TEST" in payload[f"card{selector_index}_widget1_options_text"]

    assert credentials_index is not None
    credential_widget_types = {
        payload.get(f"card{credentials_index}_widget{j}_type")
        for j in range(1, 7)
    }
    credential_action_ids = {
        payload.get(f"card{credentials_index}_widget{j}_action_id")
        for j in range(1, 7)
    }

    assert "input" in credential_widget_types
    assert "user.create" in credential_action_ids


def test_desktop_card_preview_supports_input_select_and_popup() -> None:
    text = _read('ui_qml/components/DesktopLayoutCardPreview.qml')
    for token in [
        'TextField',
        'ComboBox',
        'optionsFromText',
        'resolveArgsTemplate',
        'profilePopup',
        '${input.',
        '${select.',
        'widget1OptionsText',
    ]:
        assert token in text
    for forbidden in ['eval(', 'XMLHttpRequest', 'Loader', 'Repeater', 'Timer']:
        assert forbidden not in text


def test_desktop_layout_preview_passes_widget_options_to_cards() -> None:
    text = _read('ui_qml/components/DesktopLayoutPreview.qml')
    assert 'card1Widget1OptionsText' in text
    assert 'widget1OptionsText: root.card1Widget1OptionsText' in text
    assert 'card7Widget6OptionsText' in text
