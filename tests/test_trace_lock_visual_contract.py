from __future__ import annotations

import json
from pathlib import Path


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_trace_lock_visual_contract() -> None:
    manifest = _read_json("assets/manifest.json")
    common = manifest.get("common_assets") or {}

    required_visual_slots = [
        "tracelock.background.default",
        "tracelock.background.grid",
        "tracelock.target.marked_trace",
        "tracelock.target.burst_trace",
        "tracelock.target.unstable_trace",
        "tracelock.progress_ring.default",
        "tracelock.timer_bar.default",
        "tracelock.effect.trace_seal",
        "tracelock.effect.lock_failed",
        "tracelock.effect.trace_drop",
        "tracelock.effect.combo_popup",
        "tracelock.effect.local_ripple",
    ]
    for key in required_visual_slots:
        assert key in common, key
        desc = common[key]
        assert desc.get("task25e0_role") in {"artist_replaceable_slot", "legacy_unused_slot"}
        assert "style_key" in desc
        assert desc.get("fallback_shape") is not None

    # Fake/noise target is intentionally retained only as a legacy unused slot.
    assert common.get("tracelock.target.noise_trace", {}).get("task25e0_role") == "legacy_unused_slot"

    game_cfg = _read_json("assets/packs/default/games/trace_lock.json")
    assert game_cfg["canvas"]["background_effects"]["enabled"] is True
    assert game_cfg["progress_ring"]["asset_key"] == "tracelock.progress_ring.default"

    qml = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    for token in [
        "backgroundVfxCanvas",
        "targetImageSource",
        "progressRingImageSource",
        "effectImageSource",
        "tracelock.effect.local_ripple",
    ]:
        assert token in qml


def test_trace_lock_audio_slots_are_declared_but_do_not_touch_game_backend() -> None:
    manifest = _read_json("assets/manifest.json")
    common = manifest.get("common_assets") or {}
    for key in [
        "audio.ui.click",
        "audio.tracelock.hit",
        "audio.tracelock.miss",
        "audio.tracelock.combo",
        "audio.tracelock.music.loop",
        "audio.tracelock.ambient.loop",
    ]:
        assert key in common, key
        assert common[key].get("type") == "audio"

    backend = Path("game/examples/trace_lock/trace_lock_client.py").read_text(encoding="utf-8")
    for banned in ["assets/", "assets\\", ".png", ".jpg", ".jpeg", ".webp", ".svg"]:
        assert banned not in backend
