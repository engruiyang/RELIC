from pathlib import Path


def test_report_page_visible_structure_tokens() -> None:
    text = Path('ui_qml/pages/ReportPage.qml').read_text(encoding='utf-8')
    for token in [
        'Report Readiness',
        'Latest Report',
        'Session List',
        'Session Detail',
        'Report Action Result',
        'Refresh Report',
        'List Sessions',
        'Show Selected',
        'selected_session_id',
        'No sessions found.',
        'missing_session_id',
        'latest_report_path',
        'export_path',
        'Page Commands',
        'Page Feedback',
        'report_query_card',
        'report_detail_card',
        'report_actions_card',
        'report_popup_card',
        'report_preview',
    ]:
        assert token in text


def test_report_popup_overlay_and_shared_action_state_tokens() -> None:
    card_text = Path('ui_qml/components/DesktopLayoutCardPreview.qml').read_text(encoding='utf-8')
    preview_text = Path('ui_qml/components/DesktopLayoutPreview.qml').read_text(encoding='utf-8')

    assert 'parent: Overlay.overlay' in card_text
    assert 'sharedReportActionRaw' in card_text
    assert 'reportActionResultReady' in card_text
    assert 'lastReportActionRaw' in card_text
    assert 'reportValue(' in card_text
    assert 'Report Preview' in card_text
    assert 'report_preview' in card_text
    assert 'reportExportPathValue' in card_text
    assert 'report_list_text' in card_text
    assert 'reportListCountText' in card_text
    assert 'Current User Reports' in card_text
    assert 'Flickable {' in card_text
    assert 'reportListScrollBar' in card_text

    assert 'property string sharedReportActionRaw' in preview_text
    assert 'sharedReportActionRaw: root.sharedReportActionRaw' in preview_text
    assert 'onReportActionResultReady' in preview_text


def test_report_page_uses_native_report_actions_without_forbidden_patterns() -> None:
    text = Path('ui_qml/pages/ReportPage.qml').read_text(encoding='utf-8')
    for token in [
        'report.refresh',
        'report.latest',
        'report.list',
        'report.show',
        'report.export_txt',
        'guiBridge.invokeAction',
    ]:
        assert token in text
    for banned in [
        'GameCanvas {',
        'Loader',
        'Repeater',
        'interval: 100',
        'subprocess',
        'Popen',
        'os.system',
        'Open Path Manual',
        'Show Manual',
        'report.open_path_manual',
    ]:
        assert banned not in text


def test_report_page_tracks_wrapped_report_and_export_paths() -> None:
    text = Path('ui_qml/pages/ReportPage.qml').read_text(encoding='utf-8')
    assert 'selectedReportPath' in text
    assert 'latestReportPath' in text
    assert 'exportPath' in text
    assert 'WrapAnywhere' in text
