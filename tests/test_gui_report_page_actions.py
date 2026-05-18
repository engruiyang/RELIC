from gui.gui_facade import GuiFacade


def test_report_page_actions_feedback() -> None:
    f = GuiFacade(mode='mock')
    refresh = f.invoke_action('report.refresh', {})
    assert refresh.get('status') == 'accepted'
    assert refresh.get('message') == 'report_refreshed'
    assert isinstance(refresh.get('result'), dict)

    listing = f.invoke_action('report.list', {})
    assert listing.get('status') == 'accepted'
    assert 'items' in listing
    assert 'items_count' in listing

    missing = f.invoke_action('report.show', {})
    assert missing.get('status') == 'missing_input'
    assert missing.get('message') == 'missing_session_id'

    exported = f.invoke_action('report.export', {})
    assert exported.get('status') == 'not_implemented'
    assert exported.get('message') == 'report_export_deferred'


def test_report_show_unknown_session_is_visible() -> None:
    f = GuiFacade(mode='mock')
    result = f.invoke_action('report.show', {'session_id': 'NO_SUCH_SESSION'})
    assert result.get('status') == 'session_not_found'
    assert result.get('session_id') == 'NO_SUCH_SESSION'
