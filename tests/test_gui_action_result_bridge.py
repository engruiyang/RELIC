import json
import pytest

QtCore = pytest.importorskip("PySide6.QtCore")
from gui.gui_bridge import GuiBridge
from gui.gui_facade import GuiFacade


def test_bridge_action_result_updates() -> None:
    b = GuiBridge(GuiFacade(mode='mock'))
    for aid in ['user.list','calibration.list','report.list','game.status','devlab.run']:
        out = json.loads(b.invokeAction(aid, '{}'))
        assert out.get('action_id') == aid
        assert 'status' in out and 'message' in out
        assert aid in b.lastActionResultJson
        assert 'page_id' in b.pageActionResultJson
