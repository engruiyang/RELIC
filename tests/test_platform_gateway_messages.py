from relic_platform.platform_messages import PlatformMessageParser


def test_platform_message_to_raw_events():
    parser = PlatformMessageParser()
    payload = {
        "connected": True,
        "bridge_alive": True,
        "attention_value": 83,
        "gyro_x": 1.0,
        "gyro_y": 2.0,
        "gyro_z": 3.0,
        "focus_x": 0.2,
    }
    events = parser.to_raw_events(payload=payload, now_ms=1234)
    event_types = [e["type"] for e in events]
    assert event_types == ["device_status", "stream_status", "attention", "gyroscope"]
    assert events[2]["value"] == 83
    assert events[3]["x"] == 1.0
