from __future__ import annotations

import time
from pathlib import Path

from game.examples.trace_lock.trace_lock_client import TraceLockClient
from game.game_contracts import GameInputEvent
from gui.gui_facade import GuiFacade


def _target(view):
    return [e for e in view.entities if e.kind == "target"][0]


def _evt(x: float, y: float, ts: int) -> GameInputEvent:
    return GameInputEvent(event_id=f"e{ts}", session_id="s1", game_id="trace_lock", input_type="pointer_click", created_at_ms=ts, source="mouse", x_norm=x, y_norm=y, button=0, raw_event_type="click")


def test_debug_difficulty_maps_to_expected_movement_and_hud_xy_v() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    for lvl, mt in [(1, "static"), (3, "drift"), (4, "linear"), (5, "burst")]:
        c.set_debug_difficulty(lvl)
        hud = c.build_game_view().hud
        assert hud["movement_type"] == mt
    hud = c.build_game_view().hud
    assert {"target_x", "target_y", "target_vx", "target_vy"}.issubset(hud)


def test_movement_visible_bounds_hit_and_omitted_queue_behavior() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    c.set_debug_difficulty(5)
    v1 = c.build_game_view()
    x1, y1 = v1.hud["target_x"], v1.hud["target_y"]
    c.update({}, 120)
    c.update({}, 120)
    v2 = c.build_game_view()
    x2, y2 = v2.hud["target_x"], v2.hud["target_y"]
    assert (x1 != x2) or (y1 != y2)
    assert 0.08 <= x2 <= 0.92 and 0.08 <= y2 <= 0.92

    t = _target(v2)
    c.handle_input(_evt(t.x, t.y, 999))
    assert any(e.event_type == "target_click" for e in c.collect_game_events())

    c.start({"session_id": "s2", "difficulty": 1})
    c.update({}, 2000)
    ev1 = [e for e in c.collect_game_events() if e.event_type == "target_omitted"]
    assert len(ev1) == 1 and ev1[0].reportable is False
    ev2 = [e for e in c.collect_game_events() if e.event_type == "target_omitted"]
    assert len(ev2) == 0


def test_live_facade_tick_refresh_end_session_gate_and_fake_game() -> None:
    f = GuiFacade(mode="live-control", game_id="trace_lock")
    f.handle_gui_command("start_mock_session", {})
    f.handle_gui_command("set_debug_difficulty", {"level": 5})
    time.sleep(0.25)
    h1 = f.get_game_hud()
    x1, y1 = h1.get("target_x"), h1.get("target_y")
    time.sleep(0.25)
    h2 = f.get_game_hud()
    assert h2.get("movement_type") == "burst"
    assert (x1 != h2.get("target_x")) or (y1 != h2.get("target_y"))

    before_score, before_combo, before_acc = h2.get("score"), h2.get("combo"), h2.get("accuracy")
    before_platform = f.platform_message_count
    f.handle_gui_command("end_session", {})
    time.sleep(0.2)
    h3 = f.get_game_hud()
    assert h3.get("score") == before_score and h3.get("combo") == before_combo and h3.get("accuracy") == before_acc
    f.handle_gui_event("pointer_click", {"x_norm": 0.1, "y_norm": 0.1})
    assert f.last_event_result["result"] == "no_active_live_debug_session"
    assert f.platform_message_count == before_platform
    f.close()

    ff = GuiFacade(mode="live-control", game_id="fake_game")
    ff.handle_gui_command("start_mock_session", {})
    ff.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert ff.last_event_result["result"] == "game_event_recorded_and_platform_mocked"
    ff.close()


def test_forbidden_tokens() -> None:
    qml = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    for banned in ["PlatformReporter", "ipc_mouse_data", "AssetManager", "assets/"]:
        assert banned not in qml

    src = Path("game/examples/trace_lock/trace_lock_client.py").read_text(encoding="utf-8")
    for banned in ["AssetManager", "ThemeManager", "LayoutManager", "PlatformReporter", "ipc_mouse_data", "PySide6", "QML", "assets/"]:
        assert banned not in src
