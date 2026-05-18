from data.data_center import DataCenter


def test_data_center_starts_with_no_signal_flags() -> None:
    dc = DataCenter()
    dc.ingest_events([], now_ms=1000)
    snap = dc.get_runtime_snapshot()
    assert snap["quality"] in {"warning", "error"}
    assert "device_disconnected" in snap["error_flags"]


def test_data_center_attention_and_gyro_update_runtime_fields() -> None:
    dc = DataCenter()
    events = [
        {"type": "device_status", "connected": True, "stream_alive": True, "sensor_stream_active": True},
        {"type": "attention", "value": 65},
        {"type": "gyroscope", "x": 1.0, "y": 2.0, "z": 3.0},
    ]
    dc.ingest_events(events, now_ms=1000)
    snap = dc.get_runtime_snapshot()
    assert snap["attention"] == 65
    assert snap["gyro_x"] == 1.0
    assert snap["gyro_y"] == 2.0
    assert snap["gyro_z"] == 3.0


def test_data_center_quality_gate_application_overrides_quality_state() -> None:
    dc = DataCenter()
    dc.apply_quality_gate(
        {
            "sqi": 0.8,
            "quality_state": "ok",
            "quality_reasons": ["stable"],
            "calibration_usable": True,
            "formal_training_allowed": True,
            "signal_reliable": True,
            "estimation_allowed": True,
        }
    )
    snap = dc.get_runtime_snapshot()
    assert snap["sqi"] == 0.8
    assert snap["quality_state"] == "ok"
    assert snap["calibration_usable"] is True
