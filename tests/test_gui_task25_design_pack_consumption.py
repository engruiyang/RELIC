from pathlib import Path

def test_minimal_gui_consumes_render_resources_json() -> None:
    text = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    assert 'renderResourcesJson' in text
    assert 'pageStylesObj=renderResourcesObj.page_styles' in text
    assert 'componentStylesObj=renderResourcesObj.component_styles' in text
