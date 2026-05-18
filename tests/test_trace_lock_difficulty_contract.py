from game.examples.trace_lock.trace_lock_client import TraceLockClient


def test_tracelock_hud_exposes_difficulty_state() -> None:
    client = TraceLockClient()
    client.start({"session_id": "s1", "difficulty": 1})
    hud = client.build_game_view().hud
    assert hud["difficulty_mode"] == "auto"
    assert hud["debug_difficulty"] == "auto"
    assert hud["dynamic_difficulty_enabled"] is True

    client.set_debug_difficulty(4)
    hud2 = client.build_game_view().hud
    assert hud2["difficulty_mode"] == "manual"
    assert hud2["debug_difficulty"] == 4
    assert hud2["level"] == 4
    assert hud2["dynamic_difficulty_enabled"] is False

    client.set_debug_difficulty(None)
    hud3 = client.build_game_view().hud
    assert hud3["difficulty_mode"] == "auto"
    assert hud3["debug_difficulty"] == "auto"
    assert hud3["dynamic_difficulty_enabled"] is True
