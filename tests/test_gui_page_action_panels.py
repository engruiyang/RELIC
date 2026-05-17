from pathlib import Path

def test_page_action_panels_tokens() -> None:
    assert 'List Users' in Path('ui_qml/pages/UserPage.qml').read_text(encoding='utf-8')
    c = Path('ui_qml/pages/CalibrationPage.qml').read_text(encoding='utf-8')
    for t in ['Calibration Status','List Calibrations','Latest Calibration','Show Calibration','Bind Calibration']:
        assert t in c
    t = Path('ui_qml/pages/TrainingPage.qml').read_text(encoding='utf-8')
    assert 'Start Session' in t and 'Stop Session' in t and 'GameCanvas will be restored in TASK24' in t
    r = Path('ui_qml/pages/ReportPage.qml').read_text(encoding='utf-8')
    for x in ['List Sessions','Show Session','Latest Report','latest_report_path']:
        assert x in r
    d = Path('ui_qml/pages/DiagnosticsPage.qml').read_text(encoding='utf-8')
    for x in ['Developer Diagnostics Console','Live Input','Quality / Focus','warning_flags','error_flags']:
        assert x in d
