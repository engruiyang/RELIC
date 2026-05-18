from pathlib import Path

def test_training_page_passes_render_resources_obj() -> None:
    text = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    assert 'TrainingPage {' in text
    assert 'renderResourcesObj: root.renderResourcesObj' in text
