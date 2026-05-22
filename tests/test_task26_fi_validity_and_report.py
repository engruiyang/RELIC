from gui.gui_live_control_source import GuiLiveControlSource
from gui.gui_facade import GuiFacade


def _src() -> GuiLiveControlSource:
    return GuiLiveControlSource(game_id="trace_lock")


def test_fi_placeholder_zero_becomes_provisional() -> None:
    src = _src()
    runtime = {"fi": 0.0, "attention": 60, "attention_fresh": True, "stream_alive": True, "quality_state": "ok", "sqi": 1.0, "error_flags": [], "gyro_fresh": True}
    out = src._resolve_runtime_fi(runtime)
    assert out["fi_valid"] is True
    assert out["fi_provisional"] is True
    assert "provisional" in out["fi_source"]
    assert out["fi"] > 0


def test_calibration_affects_provisional_fi() -> None:
    src = _src()
    low = src._resolve_runtime_fi({"attention": 50, "attention_fresh": True, "stream_alive": True, "quality_state": "ok"}, calibration_profile={"attention_baseline": 50, "attention_std": 10})
    high = src._resolve_runtime_fi({"attention": 70, "attention_fresh": True, "stream_alive": True, "quality_state": "ok"}, calibration_profile={"attention_baseline": 50, "attention_std": 10})
    assert low["fi"] > 0
    assert 30 <= low["fi"] <= 80
    assert high["fi"] > low["fi"]


def test_behavior_changes_provisional_fi() -> None:
    src = _src()
    runtime = {"attention": 60, "attention_fresh": True, "stream_alive": True, "quality_state": "ok", "gyro_fresh": True}
    good = src._resolve_runtime_fi(runtime, behavior_sample={"accuracy": 0.95, "omission": 0.05, "false_action": 0.05, "rt_stability": 0.9})
    bad = src._resolve_runtime_fi(runtime, behavior_sample={"accuracy": 0.4, "omission": 0.5, "false_action": 0.4, "rt_stability": 0.3})
    assert good["fi"] > bad["fi"]


def test_control_state_derivation_not_fatigued_when_fi_over_40() -> None:
    src = _src()
    assert src._derive_control_state_from_fi(45) == "DISTRACTED"


def test_duration_sec_backfill_from_total_ms() -> None:
    facade = GuiFacade(mode="mock")
    row = facade._normalize_session_record({"session_id": "s1", "total_duration_ms": 27330})
    assert row["duration_sec"] == 27.3
