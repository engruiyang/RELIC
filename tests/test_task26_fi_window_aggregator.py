from gui.gui_live_control_source import GuiLiveControlSource


def _rows(fi=60.0, sqi=1.0, control="STABLE_FOCUS", n=20):
    base = 1_000_000
    return [
        {"now_ms": base + i * 100, "fi": fi, "fi_valid": True, "fi_provisional": True, "fi_source": "calibration_attention_behavior_provisional", "sqi": sqi, "sqi_valid": True, "quality_state": "ok", "control_state": control}
        for i in range(n)
    ]


def test_build_training_window_basic() -> None:
    src = GuiLiveControlSource(game_id="trace_lock")
    windows = src._build_training_windows(_rows(), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.8, "omission": 0.1, "false_action": 0.1, "rt_stability": 0.8, "target_count": 10, "correct_count": 8, "omission_count": 1, "false_action_count": 1}], None)
    assert windows
    w = windows[0]
    assert "window_index" in w and "fi_avg" in w and "recommended_difficulty_action" in w


def test_low_sqi_blocks_down_suggestion() -> None:
    src = GuiLiveControlSource(game_id="trace_lock")
    windows = src._build_training_windows(_rows(fi=30, sqi=0.3, control="FATIGUED"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.2, "omission": 0.7, "false_action": 0.5, "rt_stability": 0.2}], None)
    assert windows[0]["recommended_difficulty_action"] == "blocked_by_low_sqi"


def test_up_down_conflict_and_insufficient() -> None:
    src = GuiLiveControlSource(game_id="trace_lock")
    up = src._build_training_windows(_rows(fi=75, sqi=0.9, control="HIGH_FOCUS"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.9, "omission": 0.05, "false_action": 0.05, "rt_stability": 0.9}], None)[0]
    assert up["recommended_difficulty_action"] == "suggest_level_up"
    down = src._build_training_windows(_rows(fi=30, sqi=0.9, control="FATIGUED"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.3, "omission": 0.6, "false_action": 0.4, "rt_stability": 0.3}], None)[0]
    assert down["recommended_difficulty_action"] == "suggest_level_down"
    c1 = src._build_training_windows(_rows(fi=70, sqi=0.9, control="HIGH_FOCUS"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.3, "omission": 0.5, "false_action": 0.4, "rt_stability": 0.3}], None)[0]
    assert c1["recommended_difficulty_action"] == "conflict_hold"
    c2 = src._build_training_windows(_rows(fi=40, sqi=0.9, control="DISTRACTED"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.95, "omission": 0.05, "false_action": 0.05, "rt_stability": 0.95}], None)[0]
    assert c2["recommended_difficulty_action"] == "conflict_hold"
    ins = src._build_training_windows(_rows(), None, None)[0]
    assert ins["recommended_difficulty_action"] == "insufficient_samples"


def test_feedback_modes_cover() -> None:
    src = GuiLiveControlSource(game_id="trace_lock")
    assert src._build_training_windows(_rows(fi=70, sqi=0.3, control="HIGH_FOCUS"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.9, "omission": 0.1, "false_action": 0.1, "rt_stability": 0.9}], None)[0]["recommended_feedback_mode"] == "signal_check"
    assert src._build_training_windows(_rows(fi=75, sqi=0.9, control="HIGH_FOCUS"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.9, "omission": 0.1, "false_action": 0.1, "rt_stability": 0.9}], None)[0]["recommended_feedback_mode"] == "reward"
    assert src._build_training_windows(_rows(fi=62, sqi=0.9, control="STABLE_FOCUS"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.72, "omission": 0.2, "false_action": 0.2, "rt_stability": 0.7}], None)[0]["recommended_feedback_mode"] == "maintain"
    assert src._build_training_windows(_rows(fi=50, sqi=0.9, control="DISTRACTED"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.65, "omission": 0.3, "false_action": 0.25, "rt_stability": 0.55}], None)[0]["recommended_feedback_mode"] == "assist"
    assert src._build_training_windows(_rows(fi=30, sqi=0.9, control="FATIGUED"), [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.3, "omission": 0.6, "false_action": 0.4, "rt_stability": 0.3}], None)[0]["recommended_feedback_mode"] == "protect"


def test_training_window_written_jsonl(tmp_path) -> None:
    src = GuiLiveControlSource(game_id="trace_lock")
    src._training_runtime = _rows()
    windows = src._build_training_windows(src._training_runtime, [{"now_ms": 1000100, "sample_index": 0, "accuracy": 0.8, "omission": 0.1, "false_action": 0.1, "rt_stability": 0.8}], None)
    out = tmp_path / "x.jsonl"
    class V: score=1; combo=0; level=1; hud={}
    src._write_training_log(str(out), {"accuracy":0.8}, V(), 2000, windows)
    txt = out.read_text(encoding="utf-8")
    assert "\"event_type\": \"training_window\"" in txt
