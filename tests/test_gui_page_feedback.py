from pathlib import Path

def test_each_page_has_commands_and_feedback_and_no_banned() -> None:
    for p in ['HomePage','UserPage','CalibrationPage','TrainingPage','ReportPage','DiagnosticsPage','DeveloperLabPage']:
        text = Path(f'ui_qml/pages/{p}.qml').read_text(encoding='utf-8')
        assert 'Page Commands' in text
        assert 'Page Feedback' in text
    all_qml='\n'.join(Path('ui_qml').rglob('*.qml').__iter__().__next__().read_text() for _ in [0])
    full='\n'.join(Path(x).read_text(encoding='utf-8') for x in [Path('ui_qml/MinimalGui.qml')] + sorted(Path('ui_qml/pages').glob('*.qml'))) 
    for b in ['GameCanvas {','Loader','Repeater','interval: 100','subprocess','Popen','os.system']:
        assert b not in full
