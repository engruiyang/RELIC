from gui.gui_live_control_source import GuiLiveControlSource


def test_auto_mode_feedback_fields() -> None:
    src = GuiLiveControlSource(game_id='trace_lock')
    r1 = src.set_debug_difficulty(3)
    assert r1['difficulty_mode'] == 'manual'
    r2 = src.set_debug_difficulty(None)
    assert r2['difficulty_mode'] == 'auto'
    assert r2['debug_difficulty'] == 'auto'
    assert r2['dynamic_difficulty_enabled'] is True
    s = src.get_session_state()
    assert s['difficulty_mode'] == 'auto'
    assert 'dda_enabled' in s and 'latest_difficulty_decision' in s


def test_start_training_context_has_auto_flags() -> None:
    src = GuiLiveControlSource(game_id='trace_lock')
    res = src.start_training_session(difficulty_mode='auto')
    ctx = res['session_context']
    assert ctx['difficulty_mode'] == 'auto'
    assert ctx['dynamic_difficulty_enabled'] is True
    assert ctx['dda_enabled'] is True
