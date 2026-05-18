from gui.gui_facade import GuiFacade


def test_report_page_actions_feedback() -> None:
    f = GuiFacade(mode='mock')
    assert f.invoke_action('report.refresh', {}).get('status') == 'accepted'
    assert f.invoke_action('report.list', {}).get('status') == 'unsupported_in_current_mode'
    assert f.invoke_action('report.show', {}).get('status') == 'unsupported_in_current_mode'
    assert f.invoke_action('report.export', {}).get('status') == 'unsupported_in_current_mode'
