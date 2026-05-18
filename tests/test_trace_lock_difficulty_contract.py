from game.examples.trace_lock.trace_lock_client import TraceLockClient


def test_tracelock_hud_exposes_difficulty_state() -> None:
    client = TraceLockClient()
    client.start({"session_id": "s1", "difficulty": 1})
    hud = client.build_game_view().hud
    assert hud["difficulty_mode"] == "auto"
    assert hud["debug_difficulty"] == "auto"
    assert hud["dynamic_difficulty_enabled"] is True
    assert hud["game_duration_ms"] >= 15000
    assert hud["time_left_ms"] <= hud["game_duration_ms"]

    client.set_debug_difficulty(4)
    hud2 = client.build_game_view().hud
    assert hud2["difficulty_mode"] == "manual"
    assert hud2["debug_difficulty"] == 4
    assert hud2["level"] == 4
    assert hud2["dynamic_difficulty_enabled"] is False
    assert hud2["difficulty_locked"] is True

    client.set_debug_difficulty(None)
    hud3 = client.build_game_view().hud
    assert hud3["difficulty_mode"] == "auto"
    assert hud3["debug_difficulty"] == "auto"
    assert hud3["dynamic_difficulty_enabled"] is True


def test_tracelock_duration_can_be_configured_and_manual_blocks_auto_change() -> None:
    client = TraceLockClient()
    client.start({"session_id": "s2", "difficulty": 1, "game_duration_ms": 180000})
    assert client.build_game_view().hud["game_duration_ms"] == 180000
    client.set_debug_difficulty(5)
    for _ in range(20):
        client.update({"control_state": "DISTRACTED", "gyro_fresh": True}, 1000)
    hud = client.build_game_view().hud
    assert hud["difficulty_mode"] == "manual"
    assert hud["level"] == 5
    assert hud["dynamic_difficulty_enabled"] is False
