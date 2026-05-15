from __future__ import annotations

import json
from pathlib import Path

from game.examples.trace_lock.trace_lock_client import TraceLockClient
from gui.gui_facade import GuiFacade


def _target(view):
    return [e for e in view.entities if e.kind == "target"][0]


def test_tracelock_hud_and_behavior_fields_and_debug_difficulty() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    v1 = c.build_game_view()
    assert {"score", "combo", "max_combo", "level"}.issubset(v1.hud)
    t1 = _target(v1)
    assert "movement_type" in t1.metadata
    assert {"target_lifetime_ms", "target_time_left_ms", "remaining_lifetime_ratio"}.issubset(v1.hud)

    sample = c.collect_behavior_sample()
    assert {"accuracy", "omission", "false_action", "rt_stability"}.issubset(sample.to_dict().keys())

    c.set_debug_difficulty(3)
    c.update({}, 100)
    assert c.build_game_view().hud["movement_type"] != "static"

    c.set_debug_difficulty(5)
    v5 = c.build_game_view()
    assert v5.hud["level"] == 5 or v5.hud["movement_type"] == "burst"

    c.set_debug_difficulty(None)
    c.update({"control_state": "HIGH_FOCUS", "attention_fresh": True, "gyro_fresh": True}, 5100)
    assert c.build_game_view().hud["level"] >= 1


def test_gui_facade_game_hud_json_and_end_session_gate_and_fake_game() -> None:
    f = GuiFacade(mode="live-control", game_id="trace_lock")
    f.handle_gui_command("start_mock_session", {})
    hud = f.get_game_hud()
    assert hud.get("game_id") == "trace_lock"
    assert {"combo", "level", "movement_type"}.issubset(hud)
    json.dumps(hud)

    before = dict(f.get_game_hud())
    f.handle_gui_command("end_session", {})
    f.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert f.last_event_result["result"] == "no_active_live_debug_session"
    after = f.get_game_hud()
    assert after.get("score") == before.get("score")
    f.close()

    f2 = GuiFacade(mode="live-control", game_id="fake_game")
    json.dumps(f2.get_game_hud())
    f2.close()


def test_qml_and_tracelock_source_no_forbidden_tokens() -> None:
    qml = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    for banned in ["PlatformReporter", "ipc_mouse_data", "AssetManager", "assets/"]:
        assert banned not in qml

    src = Path("game/examples/trace_lock/trace_lock_client.py").read_text(encoding="utf-8")
    for banned in ["AssetManager", "ThemeManager", "LayoutManager", "PlatformReporter", "ipc_mouse_data", "PySide6", "QML", "assets/"]:
        assert banned not in src
