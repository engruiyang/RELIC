from gui.gui_facade import GuiFacade


def test_game_status_feedback_inactive_and_active() -> None:
    f = GuiFacade(mode='mock')
    r = f.invoke_action('game.status', {})
    assert 'status' in r and 'result' in r
    f.invoke_action('session.start', {})
    r2 = f.invoke_action('game.status', {})
    assert 'status' in r2
