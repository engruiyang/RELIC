from gui.gui_live_control_source import GuiLiveControlSource


def test_derive_wrapper_calls_resolve(monkeypatch):
    src = GuiLiveControlSource(game_id="trace_lock")
    called = {}
    def fake(runtime, behavior_sample=None, calibration_profile=None):
        called["args"] = (runtime, behavior_sample, calibration_profile)
        return {"fi": 12.3}
    monkeypatch.setattr(src, "_resolve_runtime_fi", fake)
    out = src._derive_fi_from_runtime({"x": 1}, {"b": 2}, {"c": 3})
    assert out == {"fi": 12.3}
    assert called["args"][0] == {"x": 1}


def test_snapshot_behavior_sample_has_timestamp():
    src = GuiLiveControlSource(game_id="trace_lock")
    s = src._snapshot_behavior_sample("pointer_click")
    assert "now_ms" in s and "sample_index" in s and s["behavior_source"] == "pointer_click"


def test_window_alignment_changes_behavior_across_windows():
    src = GuiLiveControlSource(game_id="trace_lock")
    src._training_window_ms = 500
    runtime = []
    base = 1_000_000
    for i in range(20):
        runtime.append({"now_ms": base + i * 100, "fi": 60, "fi_valid": True, "fi_provisional": True, "fi_source": "x", "sqi": 1.0, "sqi_valid": True, "quality_state": "ok", "control_state": "STABLE_FOCUS"})
    behavior = [
        {"now_ms": base + 200, "sample_index": 0, "accuracy": 0.9, "omission": 0.05, "false_action": 0.05, "rt_stability": 0.9},
        {"now_ms": base + 1200, "sample_index": 1, "accuracy": 0.4, "omission": 0.4, "false_action": 0.35, "rt_stability": 0.4},
    ]
    windows = src._build_training_windows(runtime, behavior, None)
    assert len(windows) >= 3
    assert windows[0]["accuracy_window"] != windows[2]["accuracy_window"]
    assert windows[0]["perf_window"] != windows[2]["perf_window"]


def test_carried_forward_and_session_final_and_unavailable():
    src = GuiLiveControlSource(game_id="trace_lock")
    src._training_window_ms = 500
    base = 1_000_000
    runtime = [{"now_ms": base + i * 100, "fi": 60, "fi_valid": True, "fi_provisional": True, "fi_source": "x", "sqi": 1.0, "sqi_valid": True, "quality_state": "ok", "control_state": "STABLE_FOCUS"} for i in range(10)]
    behavior = [{"now_ms": base + 100, "sample_index": 0, "accuracy": 0.8, "omission": 0.1, "false_action": 0.1, "rt_stability": 0.8}]
    w = src._build_training_windows(runtime, behavior, None)
    assert any(x["behavior_window_source"] == "carried_forward" for x in w[1:])
    w2 = src._build_training_windows(runtime, [], {"accuracy": 0.7, "omission": 0.2, "false_action": 0.2, "rt_stability": 0.7})
    assert w2[0]["behavior_window_source"] == "session_final_summary"
    w3 = src._build_training_windows(runtime, [], None)
    assert w3[0]["recommended_difficulty_action"] == "insufficient_samples"


def test_no_difficulty_mutation_from_aggregator():
    src = GuiLiveControlSource(game_id="trace_lock")
    before = src._debug_difficulty_level
    runtime = [{"now_ms": 1_000_000 + i * 100, "fi": 60, "fi_valid": True, "fi_provisional": True, "fi_source": "x", "sqi": 1.0, "sqi_valid": True, "quality_state": "ok", "control_state": "STABLE_FOCUS"} for i in range(10)]
    src._build_training_windows(runtime, [], None)
    assert src._debug_difficulty_level == before


def test_periodic_behavior_snapshot_recorded() -> None:
    src = GuiLiveControlSource(game_id="trace_lock")
    src.interaction_enabled = True
    src.session_type = "training"
    src._last_behavior_snapshot_ms = 0
    src._behavior_snapshot_interval_ms = 1
    before = len(src._training_samples)
    src._training_samples.append(src._snapshot_behavior_sample("periodic"))
    assert len(src._training_samples) == before + 1
    assert src._training_samples[-1]["behavior_source"] == "periodic"
