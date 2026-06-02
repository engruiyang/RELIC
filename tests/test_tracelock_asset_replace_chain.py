from __future__ import annotations

import json
from pathlib import Path


def _json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_tracelock_replaceable_slots_cover_targets_vfx_background_and_audio() -> None:
    manifest = _json("assets/manifest.json")
    common = manifest["common_assets"]
    required = [
        "tracelock.background.grid",
        "tracelock.target.marked_trace",
        "tracelock.target.burst_trace",
        "tracelock.target.unstable_trace",
        "tracelock.progress_ring.default",
        "tracelock.effect.trace_seal",
        "tracelock.effect.lock_failed",
        "tracelock.effect.trace_drop",
        "tracelock.effect.combo_popup",
        "tracelock.effect.local_ripple",
        "audio.tracelock.music.loop",
        "audio.tracelock.ambient.loop",
    ]
    for key in required:
        assert key in common
        assert common[key]["style_key"]
    assert common["tracelock.target.noise_trace"]["task25e0_role"] == "legacy_unused_slot"


def test_tracelock_game_style_enables_cyber_background_without_fake_targets() -> None:
    style = _json("assets/packs/default/games/trace_lock.json")
    assert style["canvas"]["background_effects"]["enabled"] is True
    assert style["canvas"]["background_effects"]["scanline_enabled"] is True
    assert style["canvas"]["background_effects"]["data_stream_enabled"] is True
    assert "burst_trace" in style["target"]
    assert "unstable_trace" in style["target"]
    assert style["target"].get("noise_trace", {}).get("legacy_unused") is True
    assert style["audio"]["music_key"] == "audio.tracelock.music.loop"


def test_game_canvas_consumes_optional_image_layers_and_local_ripple() -> None:
    text = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    for token in [
        "backgroundVfxCanvas",
        "backgroundImageSource",
        "isBackgroundImageAvailable",
        "renderResourceStyle",
        "progressRingImageSource",
        "isProgressRingImageAvailable",
        "effectAssetDescriptor",
        "effectImageSource",
        "isEffectImageAvailable",
        "tracelock.effect.local_ripple",
        "audio.tracelock.music.loop",
    ]:
        assert token in text


def test_trace_lock_backend_stays_asset_key_only_and_has_no_fake_target_spawn() -> None:
    src = Path("game/examples/trace_lock/trace_lock_client.py").read_text(encoding="utf-8")
    for banned in ["assets/", "assets\\", ".png", ".jpg", ".jpeg", ".webp", ".svg", "QML", "PySide6", "AssetManager"]:
        assert banned not in src
    assert "tracelock.target.burst_trace" in src
    assert "tracelock.target.unstable_trace" in src
    assert "tracelock.target.noise_trace" not in src
