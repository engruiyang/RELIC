from pathlib import Path

def test_real_page_files_exist_and_minimal_gui_has_pagehost() -> None:
    for p in [
        'ui_qml/pages/HomePage.qml','ui_qml/pages/UserPage.qml','ui_qml/pages/CalibrationPage.qml','ui_qml/pages/TrainingPage.qml','ui_qml/pages/ReportPage.qml','ui_qml/pages/DiagnosticsPage.qml','ui_qml/pages/DeveloperLabPage.qml'
    ]:
        assert Path(p).exists()
    qml = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    assert 'PageHost' in qml
    assert 'Developer Lab' in qml
