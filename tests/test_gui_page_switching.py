from pathlib import Path

def test_no_forbidden_gui_patterns() -> None:
    qml = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    for banned in ['GameCanvas {','Loader','Repeater','interval: 100','subprocess','ui_cli']:
        assert banned not in qml
