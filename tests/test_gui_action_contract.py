import pytest

PySide6 = pytest.importorskip("PySide6")

from pathlib import Path

from gui.gui_facade import GuiFacade
from gui.gui_bridge import GuiBridge


def test_bridge_exposes_action_contract_fields_and_slot() -> None:
    facade = GuiFacade(mode="mock")
    bridge = GuiBridge(facade)
    assert bridge.controlManifestJson
    assert bridge.controlStateJson
    result = bridge.invokeAction("app.refresh_now", "{}")
    assert "accepted" in result or "status" in result


def test_action_ids_documented() -> None:
    text = Path("docs/gui_headless_control_mapping.md").read_text(encoding="utf-8")
    for token in ["app.refresh_now", "live.reconnect", "session.start", "session.stop", "diagnostics.clear_last_error"]:
        assert token in text
