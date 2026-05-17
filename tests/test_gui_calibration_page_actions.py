from gui.gui_facade import GuiFacade


def test_calibration_actions_visible_result() -> None:
    f = GuiFacade(mode='mock')
    for action in ['calibration.status','calibration.latest','calibration.list','calibration.show','calibration.bind','calibration.cancel','calibration.start']:
        r = f.invoke_action(action, {})
        assert 'action_id' in r and 'status' in r and 'message' in r and 'result' in r
