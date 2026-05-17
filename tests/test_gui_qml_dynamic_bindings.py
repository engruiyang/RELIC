from pathlib import Path


def test_qml_dynamic_bindings_present() -> None:
    m = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    assert 'guiBridge.invokeAction' in m
    assert 'lastActionResultJson' in m

    for page in ['UserPage.qml','CalibrationPage.qml','ReportPage.qml','TrainingPage.qml','DeveloperLabPage.qml']:
        text = Path('ui_qml/pages', page).read_text(encoding='utf-8')
        assert 'PageResultPanel' in text
        assert ('PageListPanel' in text) or ('PageDetailPanel' in text)
        assert 'actionResultObj' in text

