from gui.gui_facade import GuiFacade


def test_page_actions_return_status_message_or_result() -> None:
    f = GuiFacade(mode='mock')
    for action in [
        'user.list','user.create','user.load','user.load_current','user.show_profile',
        'calibration.status','calibration.list','calibration.latest','calibration.cancel',
        'session.start','session.stop','game.status',
        'report.refresh','report.latest','report.list','report.show','report.export','report.export_txt',
        'devlab.run'
    ]:
        r = f.invoke_action(action, {'user_id': 'TEST'})
        assert isinstance(r, dict)
        assert 'status' in r
        assert 'result' in r
