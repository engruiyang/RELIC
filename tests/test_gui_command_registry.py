import json
from pathlib import Path

import pytest

from gui.command_registry import build_page_command_manifest
PySide6 = pytest.importorskip("PySide6")
from gui.gui_bridge import GuiBridge
from gui.gui_facade import GuiFacade


def _all(manifest):
    out=[]
    for items in manifest['pages'].values():
        out.extend(items)
    return out


def test_registry_manifest_and_required_coverage() -> None:
    m = build_page_command_manifest()
    assert m['schema_version'] == 'gui_commands.v1'
    ids = {c['command_id'] for c in _all(m)}
    for required in [
        'user.list','user.create','user.load','user.show_profile',
        'calibration.status','calibration.start','calibration.cancel','calibration.list','calibration.latest','calibration.show','calibration.bind',
        'training.start_session','training.stop_session','training.list_sessions','training.show_session',
        'game.debug_mock','game.debug_live','game.status',
        'developer.task6b_record_live','developer.task6b_evaluate','developer.task6b_tune'
    ]:
        assert required in ids
    for c in _all(m):
        for k in ['command_id','display_name','page_id','category','status','execution_mode','danger_level','writes_db','connects_platform','generates_files']:
            assert k in c
        if c['execution_mode'] in {'copy_only','manual'}:
            assert not c.get('native_action_id')


def test_bridge_exposes_page_command_manifest_json() -> None:
    bridge = GuiBridge(GuiFacade(mode='mock'))
    payload = json.loads(bridge.pageCommandManifestJson)
    assert payload['schema_version'] == 'gui_commands.v1'


def test_qml_has_page_commands_summary_and_banned_tokens() -> None:
    qml = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    assert 'pageCommandManifestJson' in qml
    for page_ref in ['HomePage', 'UserPage', 'CalibrationPage', 'TrainingPage', 'ReportPage', 'DiagnosticsPage', 'DeveloperLabPage']:
        assert page_ref in qml
    for page in ['HomePage.qml','UserPage.qml','CalibrationPage.qml','TrainingPage.qml','ReportPage.qml','DiagnosticsPage.qml','DeveloperLabPage.qml']:
        text = Path('ui_qml/pages/' + page).read_text(encoding='utf-8')
        assert 'Page Commands' in text
    for banned in ['subprocess', 'Popen', 'os.system', 'GameCanvas {', 'Loader', 'Repeater', 'interval: 100']:
        assert banned not in qml
