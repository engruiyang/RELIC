from __future__ import annotations

import json
from pathlib import Path


def test_minimal_gui_passes_design_pack_props_to_all_top_pages() -> None:
    text = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    for page, style in [
        ('HomePage', 'home_page'), ('UserPage', 'user_page'), ('CalibrationPage', 'calibration_page'),
        ('TrainingPage', 'training_page'), ('ReportPage', 'report_page'), ('DiagnosticsPage', 'diagnostics_page'),
        ('DeveloperLabPage', 'developer_lab_page'),
    ]:
        assert f'{page} ' in text
        assert 'designThemeObj: root.designThemeObj' in text
        assert f'pageStyleObj: root.pageStylesObj.{style}' in text
        assert 'componentStyleObj: root.componentStylesObj' in text
        assert 'renderResourcesObj: root.renderResourcesObj' in text


def test_each_top_page_has_design_background_and_required_props() -> None:
    for name in ['HomePage.qml','UserPage.qml','CalibrationPage.qml','TrainingPage.qml','ReportPage.qml','DiagnosticsPage.qml','DeveloperLabPage.qml']:
        t = Path('ui_qml/pages', name).read_text(encoding='utf-8')
        for prop in ['property var designThemeObj', 'property var pageStyleObj', 'property var componentStyleObj', 'property var renderResourcesObj']:
            assert prop in t
        assert 'DesignBackground {' in t


def test_all_pack_page_jsons_have_layered_asset_key_fit_opacity() -> None:
    pages = ['app_shell','home_page','user_page','calibration_page','training_page','report_page','diagnostics_page','developer_lab_page']
    for p in pages:
        obj = json.loads(Path(f'assets/packs/default/pages/{p}.json').read_text(encoding='utf-8'))
        layered = obj['layered']
        assert 'image' in layered and 'asset_key' in layered['image']
        assert 'fit' in layered['image']
        assert 'opacity' in layered


def test_manifest_has_background_slots() -> None:
    manifest = json.loads(Path('assets/manifest.json').read_text(encoding='utf-8'))
    common = manifest['common_assets']
    for key in ['background.home.main','background.user.main','background.calibration.main','background.training.main','background.report.main','background.diagnostics.main','background.developer_lab.main']:
        assert key in common


def test_header_feedback_use_design_tokens_and_no_forbidden_runtime_calls() -> None:
    header = Path('ui_qml/components/PageHeader.qml').read_text(encoding='utf-8')
    feedback = Path('ui_qml/components/PageFeedbackPanel.qml').read_text(encoding='utf-8')
    assert 'designThemeObj' in header
    assert 'componentStyleObj' in header
    assert 'designThemeObj' in feedback
    assert 'feedbackStyleObj' in feedback
    for path in Path('ui_qml').rglob('*.qml'):
        text = path.read_text(encoding='utf-8')
        assert 'subprocess' not in text and 'Popen' not in text and 'os.system' not in text


def test_no_new_loader_or_interval_100_outside_game_canvas() -> None:
    for path in Path('ui_qml').rglob('*.qml'):
        if path.name == 'GameCanvas.qml':
            continue
        text = path.read_text(encoding='utf-8')
        assert 'Loader {' not in text
        assert 'interval: 100' not in text
