import json

from gui.gui_protocol import GuiPacket


def test_gui_packet_serializable() -> None:
    packet = GuiPacket(type="app_state", version=1, seq=7, timestamp_ms=123, payload={"state": "READY"})
    data = packet.to_dict()
    assert data["type"] == "app_state"
    assert json.loads(json.dumps(data))["payload"]["state"] == "READY"
