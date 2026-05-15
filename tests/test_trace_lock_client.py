from __future__ import annotations

import json
from pathlib import Path

from game.examples.trace_lock.trace_lock_client import TraceLockClient
from game.game_contracts import GameInputEvent


def _evt(*, x: float, y: float, ts: int, session_id: str = "s1") -> GameInputEvent:
    return GameInputEvent(
        event_id=f"e{ts}",
        session_id=session_id,
        game_id="trace_lock",
        input_type="pointer_click",
        created_at_ms=ts,
        source="mouse",
        x_norm=x,
        y_norm=y,
        button=0,
        raw_event_type="click",
    )


def test_trace_lock_client_core_contracts() -> None:
    c = TraceLockClient()
    assert c.game_id == "trace_lock"
    c.start({"session_id": "s1", "difficulty": 1})
    assert c.get_score() == 0

    view = c.build_game_view()
    kinds = {e.kind for e in view.entities}
    assert {"target", "focus_zone", "progress_ring", "timer_bar"}.issubset(kinds)
    target = [e for e in view.entities if e.kind == "target"][0]
    assert target.asset_key.startswith("tracelock.")
    assert target.style_key.startswith("tracelock.")


def test_hit_background_timeout_and_combo_rules() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    view = c.build_game_view()
    target = [e for e in view.entities if e.kind == "target"][0]

    c.handle_input(_evt(x=target.x, y=target.y, ts=100))
    events = c.collect_game_events()
    hit = [e for e in events if e.event_type == "target_click"][0]
    assert hit.payload["target_index"] == 0
    assert hit.reportable is True

    c.handle_input(_evt(x=0.01, y=0.01, ts=200))
    events = c.collect_game_events()
    bg = [e for e in events if e.event_type == "background_click"][0]
    assert bg.payload["target_index"] == 1

    c.update({}, 5000)
    events = c.collect_game_events()
    omitted = [e for e in events if e.event_type == "target_omitted"]
    assert omitted and omitted[0].reportable is False

    sample = c.collect_behavior_sample()
    assert sample.accuracy >= 0.0
    assert sample.false_action >= 0.0
    assert sample.rt_stability >= 0.0


def test_runtime_snapshot_hint_priority_and_stable_focus() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1"})

    c.update({"attention_fresh": False}, 16)
    assert c.build_game_view().hud["hint"] in {"focus_sync_pending", "attention_stale"}

    c.update({"gyro_fresh": False}, 16)
    assert c.build_game_view().hud["hint"] in {"gyro_link_unstable", "motion_unstable"}

    c.update({"control_state": "HIGH_FOCUS", "attention_fresh": True, "gyro_fresh": True}, 16)
    sample = c.collect_behavior_sample()
    assert sample.game_specific["stable_focus_frames"] >= 1


def test_level_change_completed_visualevent_and_manifest_checks() -> None:
    c = TraceLockClient()
    c.start({"session_id": "s1", "difficulty": 1})
    for i in range(6):
        c.update({"attention_fresh": True, "gyro_fresh": True}, 100)
        v = c.build_game_view()
        t = [e for e in v.entities if e.kind == "target"][0]
        c.handle_input(_evt(x=t.x, y=t.y, ts=(i + 1) * 100))
    c.update({"attention_fresh": True, "gyro_fresh": True}, 5100)
    events = c.collect_game_events()
    assert any(e.event_type == "level_changed" for e in events)

    view = c.build_game_view()
    assert json.dumps([ve.to_dict() for ve in view.visual_events])

    c.update({}, 30000)
    events = c.collect_game_events()
    done = [e for e in events if e.event_type == "game_completed"]
    assert done and done[0].reportable is False

    manifest_path = Path("game/examples/trace_lock/manifest.example.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["game_id"] == "trace_lock"
    text = manifest_path.read_text(encoding="utf-8")
    for banned in ["assets/", ".png", ".webp", ".svg"]:
        assert banned not in text


def test_no_forbidden_imports_or_paths() -> None:
    src = Path("game/examples/trace_lock/trace_lock_client.py").read_text(encoding="utf-8")
    for banned in [
        "PlatformReporter",
        "AssetManager",
        "ThemeManager",
        "LayoutManager",
        "PySide6",
        "QML",
        "SQLite",
        "DataCenter",
        "SessionManager",
        "assets/",
        ".png",
        ".webp",
        ".svg",
    ]:
        assert banned not in src
