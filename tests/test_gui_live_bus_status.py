from __future__ import annotations

from pathlib import Path


def test_live_bus_status_fields_and_bridge_sources_exist() -> None:
    qml = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")

    for token in [
        "guiBridge.appState",
        "guiBridge.runtimeSnapshot",
        "guiBridge.sessionState",
        "guiBridge.gameHudJson",
        "connection_status",
        "stream_alive",
        "device_connected",
        "attention",
        "attention_fresh",
        "attention_age_ms",
        "attention_last_update_ms",
        "gyro_x",
        "gyro_y",
        "gyro_z",
        "gyro_fresh",
        "gyro_age_ms",
        "gyro_last_update_ms",
        "session_type",
        "session_id",
        "latest_report_path",
        "warning_flags",
        "error_flags",
    ]:
        assert token in qml


def test_live_bus_status_has_fallback_and_json_tolerance() -> None:
    qml = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    assert "safeJsonParse" in qml
    assert "try {" in qml
    assert '"n/a"' in qml
    assert "getField" in qml
    assert "__parse_error__" in qml
