from device.adapters.mock_adapter import MockAdapter


def _has_event(events: list[dict], et: str) -> bool:
    return any(e.get("type") == et for e in events)


def test_normal_mode_emits_status_and_gyro() -> None:
    m = MockAdapter(mode="normal")
    ev = m.read()
    assert _has_event(ev, "device_status")
    assert _has_event(ev, "stream_status")
    assert _has_event(ev, "gyroscope")


def test_attention_missing_start_no_attention_early_ticks() -> None:
    m = MockAdapter(mode="attention_missing_start")
    for _ in range(20):
        ev = m.read()
        assert not _has_event(ev, "attention")


def test_attention_short_dropout_drops_in_window() -> None:
    m = MockAdapter(mode="attention_short_dropout")
    missing_seen = False
    for _ in range(70):
        ev = m.read()
        if 25 <= m.tick <= 65 and not _has_event(ev, "attention"):
            missing_seen = True
    assert missing_seen


def test_attention_long_lost_stops_after_threshold() -> None:
    m = MockAdapter(mode="attention_long_lost")
    for _ in range(30):
        ev = m.read()
    assert not _has_event(ev, "attention")


def test_gyro_short_dropout_has_gap() -> None:
    m = MockAdapter(mode="gyro_short_dropout")
    missing = False
    for _ in range(35):
        ev = m.read()
        if 15 <= m.tick <= 30 and not _has_event(ev, "gyroscope"):
            missing = True
    assert missing


def test_stream_drop_mode_emits_inactive_stream() -> None:
    m = MockAdapter(mode="stream_drop")
    for _ in range(25):
        ev = m.read()
    stream = next(e for e in ev if e.get("type") == "stream_status")
    assert stream["alive"] is False and stream["active"] is False


def test_reconnect_recovery_transitions_stream_status() -> None:
    m = MockAdapter(mode="reconnect_recovery")
    saw_down = False
    saw_up = False
    for _ in range(90):
        ev = m.read()
        stream = next(e for e in ev if e.get("type") == "stream_status")
        saw_down = saw_down or (stream.get("alive") is False)
        saw_up = saw_up or (stream.get("alive") is True and m.tick > 80)
    assert saw_down and saw_up


def test_poll_compatibility_accepts_mode_override() -> None:
    m = MockAdapter(mode="normal")
    ev = m.poll(mode="stream_drop")
    assert isinstance(ev, list)
    assert m.mode == "stream_drop"
