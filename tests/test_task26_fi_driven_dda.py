from gui.gui_live_control_source import GuiLiveControlSource


def _win(i, action, sqi=1.0, fi=70, perf=0.8, signal='open'):
    return {"window_index": i, "window_end_ms": 1000 + i * 5000, "recommended_difficulty_action": action, "sqi_avg": sqi, "fi_avg": fi, "perf_window": perf, "signal_gate_status": signal, "accuracy_window": 0.8, "omission_window": 0.1, "false_action_window": 0.1, "rt_stability_window": 0.8, "decision_confidence": 0.8, "behavior_window_source": "window_snapshot", "control_state_summary": "STABLE_FOCUS:10"}


def _src(mode='auto', level=3):
    s = GuiLiveControlSource(game_id='trace_lock')
    s._difficulty_mode = mode
    s._dda_state = {"enabled": True, "last_decision_ms": 0, "cooldown_ms": 10000, "min_level": 1, "max_level": 5, "current_level": level, "pending_up_count": 0, "pending_down_count": 0, "decision_events": [], "cooldown_block_count": 0, "conflict_hold_count": 0, "low_sqi_block_count": 0}
    return s


def test_wrapper_exists_and_calls(monkeypatch):
    s = _src()
    monkeypatch.setattr(s, '_resolve_runtime_fi', lambda runtime, behavior_sample=None, calibration_profile=None: {'ok': True, 'runtime': runtime})
    out = s._derive_fi_from_runtime({'a': 1})
    assert out['ok'] is True


def test_manual_no_apply():
    s = _src(mode='manual', level=3)
    d1 = s._process_window_decision(_win(0, 'suggest_level_up'))
    d2 = s._process_window_decision(_win(1, 'suggest_level_up'))
    assert d1['applied'] is False and d2['applied'] is False
    assert s._dda_state['current_level'] == 3


def test_auto_two_consecutive_up_and_cooldown():
    s = _src(mode='auto', level=3)
    d1 = s._process_window_decision(_win(0, 'suggest_level_up'))
    d2 = s._process_window_decision(_win(1, 'suggest_level_up'))
    assert d1['applied'] is False
    assert d2['applied'] is True
    assert d2['applied_action'] == 'level_up'
    assert d2['to_level'] == d2['from_level'] + 1 or d2['to_level'] == 2
    assert d2['reason'] == 'consecutive_level_up'
    d3 = s._process_window_decision(_win(2, 'suggest_level_up'))
    assert d3['applied'] is False
    assert d3['reason'] in {'cooldown_active', 'waiting_for_consecutive_windows', 'level_limit_reached', 'hold'}


def test_down_block_conflict_insufficient_and_clamp():
    s = _src(mode='auto', level=1)
    s._process_window_decision(_win(0, 'suggest_level_down', fi=30, perf=0.3))
    d2 = s._process_window_decision(_win(1, 'suggest_level_down', fi=30, perf=0.3))
    assert d2['applied'] is False
    db = s._process_window_decision(_win(2, 'blocked_by_low_sqi', sqi=0.2, signal='blocked'))
    assert db['applied'] is False
    dc = s._process_window_decision(_win(3, 'conflict_hold'))
    assert dc['applied'] is False
    di = s._process_window_decision(_win(4, 'insufficient_samples'))
    assert di['applied'] is False
