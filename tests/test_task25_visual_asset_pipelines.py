from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path('.')
COMP = ROOT / 'ui_qml' / 'components'
PAGES = ROOT / 'ui_qml' / 'pages'
PACK = ROOT / 'assets' / 'packs' / 'default'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def test_button_asset_pipeline_is_wired() -> None:
    button = _json(PACK / 'components' / 'button.json')
    assert button['normal']['asset_key'] == 'ui.button.primary.normal'
    assert button['pressed']['asset_key'] == 'ui.button.primary.pressed'
    assert button['disabled']['asset_key'] == 'ui.button.primary.disabled'

    qml = _read(COMP / 'DesignButton.qml')
    for token in [
        'renderResourcesObj',
        'buttonAssetKey',
        'buttonImageSource',
        'assetDescriptor',
        'normalizedAssetUrl',
        'Qt.resolvedUrl("../../assets/" + u)',
        'Image {',
        'normal/pressed/disabled asset_key',
    ]:
        assert token in qml

    minimal = _read(ROOT / 'ui_qml' / 'MinimalGui.qml')
    assert 'DesignButton {' in minimal
    assert 'renderResourcesObj: root.renderResourcesObj' in minimal

    for page in [
        'HomePage.qml',
        'UserPage.qml',
        'CalibrationPage.qml',
        'TrainingPage.qml',
        'ReportPage.qml',
        'DiagnosticsPage.qml',
        'DeveloperLabPage.qml',
    ]:
        text = _read(PAGES / page)
        assert 'DesignButton {' in text, page
        assert 'renderResourcesObj:' in text, page
        assert re.search(r'(?<!Design)Button\s*\{', text) is None, page


def test_panel_header_feedback_asset_pipelines_are_wired() -> None:
    panel = _json(PACK / 'components' / 'panel.json')
    assert 'background_asset_key' in panel
    assert panel['frame_asset_key'] == 'ui.panel.frame'
    panel_qml = _read(COMP / 'DesignPanel.qml')
    for token in ['renderResourcesObj', 'background_asset_key', 'frame_asset_key', 'assetSource', 'Image {']:
        assert token in panel_qml

    header = _json(PACK / 'components' / 'header.json')
    assert header['decorator_asset_key'] == 'ui.header.decorator'
    header_qml = _read(COMP / 'PageHeader.qml')
    for token in ['renderResourcesObj', 'decorator_asset_key', 'assetSource', 'Image {']:
        assert token in header_qml

    feedback = _json(PACK / 'components' / 'feedback_panel.json')
    assert feedback['success_asset_key'] == 'ui.feedback.success'
    assert feedback['warning_asset_key'] == 'ui.feedback.warning'
    assert feedback['error_asset_key'] == 'ui.feedback.error'
    feedback_qml = _read(COMP / 'PageFeedbackPanel.qml')
    for token in ['renderResourcesObj', 'success_asset_key', 'warning_asset_key', 'error_asset_key', 'statusAssetKey', 'Image {']:
        assert token in feedback_qml
    assert 'background:' not in feedback_qml
    assert 'GroupBox' not in feedback_qml
    assert 'Control' not in feedback_qml

    for page in [
        'HomePage.qml',
        'UserPage.qml',
        'CalibrationPage.qml',
        'TrainingPage.qml',
        'ReportPage.qml',
        'DiagnosticsPage.qml',
        'DeveloperLabPage.qml',
    ]:
        text = _read(PAGES / page)
        assert 'PageHeader {' in text
        assert 'PageFeedbackPanel {' in text
        assert 'renderResourcesObj:' in text


def test_game_canvas_and_background_share_resolved_asset_urls() -> None:
    bg = _read(COMP / 'DesignBackground.qml')
    canvas = _read(COMP / 'GameCanvas.qml')
    for text in [bg, canvas]:
        assert 'Qt.resolvedUrl("../../assets/" + u)' in text
        assert 'placeholder://' in text
        assert 'renderResourcesObj.assets' in text
    assert 'return Number(root.value(layer, "opacity", 1.0))' in bg

    trace_lock = _json(PACK / 'games' / 'trace_lock.json')
    image_layers = [l for l in trace_lock['canvas']['background']['layers'] if l.get('type') == 'image']
    assert image_layers
    assert image_layers[0]['asset_key'] == 'tracelock.background.grid'
    assert float(image_layers[0]['opacity']) > 0.0


def test_no_dangerous_qml_patterns_in_visual_pipeline_files() -> None:
    files = list((ROOT / 'ui_qml').rglob('*.qml'))
    for path in files:
        text = _read(path)
        for forbidden in ['subprocess', 'Popen', 'os.system']:
            assert forbidden not in text, f'{forbidden} in {path}'


def test_design_button_exposes_pressed_signal_for_legacy_handlers() -> None:
    text = Path("ui_qml/components/DesignButton.qml").read_text(encoding="utf-8")
    assert "signal pressed()" in text
    assert "signal released()" in text
    assert "onPressed: root.pressed()" in text
    assert "readonly property bool down" in text
    assert "readonly property bool pressed" not in text
