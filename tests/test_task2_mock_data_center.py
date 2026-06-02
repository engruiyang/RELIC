from data.data_center import DataCenter
from device.adapters.mock_adapter import MockAdapter


TICK_MS = 50


def _run(mode: str, ticks: int):
    adapter = MockAdapter(mode=mode)
    dc = DataCenter()
    snapshots = []
    now = 0
    for _ in range(ticks):
        now += TICK_MS
        dc.ingest_events(adapter.read(), now_ms=now)
        snapshots.append(dc.get_runtime_snapshot())
    return snapshots


def test_normal_mode_quality_ok_and_valid():
    snaps = _run("normal", 60)
    last = snaps[-1]
    assert last["quality"] == "ok"
    assert last["training_data_valid"] is True
    assert last["control_data_valid"] is True

    att_ages = [s["attention_age_ms"] for s in snaps if s["attention_age_ms"] is not None]
    assert max(att_ages) > min(att_ages)


def test_attention_missing_start():
    snaps = _run("attention_missing_start", 20)
    last = snaps[-1]
    assert last["attention"] is None
    assert last["attention_seen_once"] is False
    assert last["attention_age_ms"] is None
    assert last["training_data_valid"] is False
    assert last["control_data_valid"] is False
    assert last["quality"] == "warning"
    assert "attention_missing" in last["warning_flags"]


def test_attention_short_dropout_warning_not_error():
    snaps = _run("attention_short_dropout", 80)
    stale = [s for s in snaps if "attention_stale" in s["warning_flags"]]
    assert stale
    s = stale[-1]
    assert s["quality"] == "warning"
    assert s["control_data_valid"] is False
    assert "attention_lost" not in s["error_flags"]


def test_attention_long_lost_error():
    snaps = _run("attention_long_lost", 160)
    lost = [s for s in snaps if "attention_lost" in s["error_flags"]]
    assert lost
    s = lost[-1]
    assert s["quality"] == "error"
    assert s["training_data_valid"] is False
    assert s["control_data_valid"] is False


def test_gyro_short_dropout_warning_not_error():
    snaps = _run("gyro_short_dropout", 40)
    stale = [s for s in snaps if "gyro_stale" in s["warning_flags"]]
    assert stale
    s = stale[-1]
    assert s["quality"] == "warning"
    assert s["control_data_valid"] is False
    assert "gyro_lost" not in s["error_flags"]


def test_stream_drop_invalid():
    snaps = _run("stream_drop", 30)
    dropped = [s for s in snaps if s["stream_alive"] is False]
    assert dropped
    s = dropped[-1]
    assert s["sensor_stream_active"] is False
    assert "stream_inactive" in s["quality_reasons"]
    assert s["training_data_valid"] is False
    assert s["control_data_valid"] is False
