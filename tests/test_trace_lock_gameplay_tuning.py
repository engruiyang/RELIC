from __future__ import annotations

from pathlib import Path

from game.examples.trace_lock.trace_lock_client import TraceLockClient
from game.game_contracts import GameInputEvent
from gui.gui_facade import GuiFacade


def _evt(x: float, y: float, ts: int) -> GameInputEvent:
    return GameInputEvent(event_id=f"e{ts}", session_id="s1", game_id="trace_lock", input_type="pointer_click", created_at_ms=ts, source="mouse", x_norm=x, y_norm=y, button=0, raw_event_type="click")


def test_time_pressure_metadata_and_progress_decrease() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    v1 = c.build_game_view()
    t1 = [e for e in v1.entities if e.kind == "target"][0]
    r1 = [e for e in v1.entities if e.kind == "progress_ring"][0]
    assert "time_left_ms" in t1.metadata and "target_lifetime_ms" in t1.metadata and "remaining_lifetime_ratio" in t1.metadata
    assert "time_left_ms" in r1.metadata and "target_lifetime_ms" in r1.metadata
    c.update({}, 400)
    v2 = c.build_game_view()
    r2 = [e for e in v2.entities if e.kind == "progress_ring"][0]
    assert r2.metadata["progress"] < r1.metadata["progress"]
    assert "target_time_left_ms" in v2.hud and "target_lifetime_ms" in v2.hud and "target_pressure_level" in v2.hud


def test_timeout_event_non_reportable() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    c.update({}, 2000)
    events = c.collect_game_events()
    omitted = [e for e in events if e.event_type == "target_omitted"]
    assert omitted and omitted[0].reportable is False


def test_movement_types_and_bounds_and_hit_on_moved_position() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    assert [e for e in c.build_game_view().entities if e.kind == "target"][0].metadata["movement_type"] == "static"

    c.start({"session_id": "s1", "difficulty": 3})
    v = c.build_game_view()
    t = [e for e in v.entities if e.kind == "target"][0]
    assert t.metadata["movement_type"] != "static"
    x0, y0 = t.x, t.y
    c.update({}, 300)
    t2 = [e for e in c.build_game_view().entities if e.kind == "target"][0]
    assert (t2.x, t2.y) != (x0, y0)
    assert 0.08 <= t2.x <= 0.92 and 0.08 <= t2.y <= 0.92

    c.handle_input(_evt(t2.x, t2.y, 500))
    events = c.collect_game_events()
    assert any(e.event_type == "target_click" for e in events)


def test_combo_multiplier_and_background_reset() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    score_deltas = []
    for i in range(11):
        t = [e for e in c.build_game_view().entities if e.kind == "target"][0]
        c.handle_input(_evt(t.x, t.y, i + 1))
        hit = [e for e in c.collect_game_events() if e.event_type == "target_click"][0]
        score_deltas.append(hit.payload["score_delta"])
    assert score_deltas[0] == 1 and 2 in score_deltas and 3 in score_deltas
    c.handle_input(_evt(0.0, 0.0, 999))
    c.collect_game_events()
    assert c.build_game_view().combo == 0


def test_end_session_gate_and_forbidden_imports_and_fake_game_live_control() -> None:
    facade = GuiFacade(mode="live-control", game_id="trace_lock")
    facade.handle_gui_command("start_mock_session", {})
    before_score = facade.get_game_view().get("score", 0)
    facade.handle_gui_command("end_session", {})
    facade.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert facade.last_event_result["result"] == "no_active_live_debug_session"
    assert facade.get_game_view().get("score", 0) == before_score
    facade.close()

    src = Path("game/examples/trace_lock/trace_lock_client.py").read_text(encoding="utf-8")
    for bad in ["AssetManager", "ThemeManager", "LayoutManager", "PlatformReporter", "ipc_mouse_data", "PySide6", "QML", "assets/"]:
        assert bad not in src

    f2 = GuiFacade(mode="live-control", game_id="fake_game")
    f2.handle_gui_command("start_mock_session", {})
    f2.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert f2.last_event_result["result"] == "game_event_recorded_and_platform_mocked"
    f2.close()
