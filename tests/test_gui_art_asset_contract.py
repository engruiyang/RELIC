import json
from pathlib import Path

def test_asset_contract_files_and_keys() -> None:
    manifest = json.loads(Path('assets/manifest.json').read_text(encoding='utf-8'))
    keys = manifest['task23_asset_contract'].keys()
    for k in ['app.logo','app.background','nav.home_icon','nav.user_icon','nav.calibration_icon','nav.training_icon','nav.report_icon','nav.diagnostics_icon','training.game_placeholder','training.fragment_lock_icon','training.signal_hunter_icon','training.stabilizer_icon','status.success_icon','status.warning_icon','status.error_icon']:
        assert k in keys
    for p in ['assets/layouts/app_shell.json','assets/layouts/home_page.json','assets/layouts/user_profile_page.json','assets/layouts/calibration_page.json','assets/layouts/training_page.json','assets/layouts/report_page.json','assets/layouts/diagnostics_page.json']:
        assert Path(p).exists()
