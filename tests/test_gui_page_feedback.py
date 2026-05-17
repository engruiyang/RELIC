from pathlib import Path

def test_each_page_has_commands_and_feedback_and_no_banned() -> None:
    for p in ['HomePage','UserPage','CalibrationPage','TrainingPage','ReportPage','DiagnosticsPage','DeveloperLabPage']:
        text = Path(f'ui_qml/pages/{p}.qml').read_text(encoding='utf-8')
        assert 'Page Commands' in text
        assert 'Page Feedback' in text
    qml_files = [Path('ui_qml/MinimalGui.qml')] + sorted(Path('ui_qml/pages').glob('*.qml'))
    full = '\n'.join(p.read_text(encoding='utf-8') for p in qml_files)
    for b in ['GameCanvas {','Loader','Repeater','interval: 100','subprocess','Popen','os.system']:
        assert b not in full
