from pathlib import Path


def test_pages_reference_dynamic_panels_and_avoid_forbidden_patterns() -> None:
    pages = [
        'ui_qml/pages/UserPage.qml',
        'ui_qml/pages/CalibrationPage.qml',
        'ui_qml/pages/TrainingPage.qml',
        'ui_qml/pages/ReportPage.qml',
        'ui_qml/pages/DiagnosticsPage.qml',
        'ui_qml/pages/DeveloperLabPage.qml',
    ]
    for p in pages:
        text = Path(p).read_text(encoding='utf-8')
        assert 'PageResultPanel' in text
        assert 'PageListPanel' in text
        assert 'PageDetailPanel' in text
        assert 'Loader' not in text
        assert 'Repeater' not in text
        assert 'GameCanvas {' not in text
        assert 'subprocess' not in text
        assert 'interval: 100' not in text
