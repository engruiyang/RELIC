from gui.gui_facade import GuiFacade


def test_user_page_actions_feedback() -> None:
    f = GuiFacade(mode='mock')
    assert f.invoke_action('user.list', {}).get('status') == 'accepted'
    assert f.invoke_action('user.create', {}).get('status') == 'missing_input'
    assert f.invoke_action('user.load', {'user_id': 'TEST'}).get('status') in {'user_loaded','missing_input'}
    assert 'status' in f.invoke_action('user.load_current', {})
