from gui.gui_facade import GuiFacade


def test_report_page_actions_feedback() -> None:
    f = GuiFacade(mode='mock')
    assert f.invoke_action('report.refresh', {}).get('status') == 'accepted'
    assert f.invoke_action('report.list', {}).get('status') == 'no_report_available'
    assert f.invoke_action('report.show', {}).get('status') == 'missing_input'
    assert f.invoke_action('report.export', {}).get('status') == 'not_implemented_in_this_task'
