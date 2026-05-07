import unittest, tempfile, json
from pathlib import Path
from relic_core.session import SessionManager
from relic_core.assets import AssetManager
class T(unittest.TestCase):
    def test_session_assets(self):
        with tempfile.TemporaryDirectory() as d:
            sm=SessionManager(base_dir=f'{d}/logs'); info=sm.start_session('empty_game'); sm.write_game_event('x',snapshot={'attention_value':1}); sm.end_session(); sm.close()
            self.assertTrue(Path(info.event_log_path).exists()); self.assertTrue(Path(info.summary_path).exists())
            am=AssetManager(root=d); self.assertIsNotNone(am.get_theme()); self.assertFalse(am.asset_exists('images.logo'))
if __name__=='__main__': unittest.main()
