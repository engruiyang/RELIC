from pathlib import Path


def test_minimal_qml_has_control_panel_and_buttons() -> None:
    qml = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    for token in [
        "Control Panel", "Refresh", "Reconnect", "Safe Stop", "Start Session", "Stop Session", "Calibration Status", "Game Status",
        "invokeAction", "controlManifestJson", "controlStateJson", "last_command", "last_command_result", "last_command_error", "command_count",
    ]:
        assert token in qml
    for banned in ["interval: 100", "ScrollView", "GameCanvas {", "Loader", "Repeater"]:
        assert banned not in qml
