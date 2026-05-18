from gui.gui_facade import GuiFacade


def test_game_status_feedback_inactive_and_active() -> None:
    f = GuiFacade(mode='mock')
    r = f.invoke_action('game.status', {})
    assert 'status' in r and 'result' in r
    f.invoke_action('session.start', {})
    r2 = f.invoke_action('game.status', {})
    assert 'status' in r2


def test_training_uses_existing_session_and_calibration_actions() -> None:
    f = GuiFacade(mode='mock')
    for action in ['user.show_profile', 'calibration.status', 'session.status', 'session.start', 'session.stop', 'game.status']:
        r = f.invoke_action(action, {'user_id': 'demo_user'})
        assert isinstance(r, dict)
        assert 'status' in r
        assert 'result' in r


def test_training_game_view_contract_fields() -> None:
    f = GuiFacade(mode='core-control', duration_sec=1)
    f.handle_gui_command('start_mock_session', {})
    f.handle_gui_event('pointer_click', {'game_id': 'fake_game', 'x_norm': 0.5, 'y_norm': 0.5, 'button': 'left', 'source': 'test'})
    view = f.get_game_view()
    assert isinstance(view, dict)
    assert 'entities' in view
    hud = f.get_game_hud()
    assert 'game_id' in hud
    f.close()
