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
        'Show Selected Session',
        'selected_session_id',
        'No sessions found.',
        'missing_session_id',
        'latest_report_path',
        'Page Commands',
        'Page Feedback',
    ]:
        assert token in text


def test_report_page_uses_native_report_actions_without_forbidden_patterns() -> None:
    text = Path('ui_qml/pages/ReportPage.qml').read_text(encoding='utf-8')
    for token in [
        'report.refresh',
        'report.list',
        'report.show',
        'report.export',
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
    ]:
        assert banned not in text
