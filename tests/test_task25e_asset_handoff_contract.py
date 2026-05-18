from __future__ import annotations

import json
from pathlib import Path

from core.resource_managers import build_render_resource_bundle, validate_design_pack_asset_handoff


PACK_ROOT = Path("assets/packs/default")
MANIFEST = Path("assets/manifest.json")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task25e0_asset_handoff_files_and_directories_exist() -> None:
    assert (PACK_ROOT / "asset_handoff.json").exists()
    for rel in [
        "images/backgrounds/.gitkeep",
        "images/ui/.gitkeep",
        "images/trace_lock/.gitkeep",
        "images/effects/.gitkeep",
        "audio/ui/.gitkeep",
        "audio/trace_lock/.gitkeep",
        "fonts/.gitkeep",
    ]:
        assert (PACK_ROOT / rel).exists(), rel


def test_task25e0_manifest_contains_artist_replaceable_slots() -> None:
    manifest = _load_json(MANIFEST)
    common = manifest["common_assets"]
    required = [
        "background.app.main",
        "background.home.main",
        "background.user.main",
        "background.calibration.main",
        "background.training.main",
        "background.report.main",
        "background.diagnostics.main",
        "background.developer_lab.main",
        "ui.logo.main",
        "ui.button.primary.normal",
        "ui.button.primary.pressed",
        "ui.button.primary.disabled",
        "tracelock.background.grid",
        "tracelock.target.marked_trace",
        "tracelock.target.noise_trace",
        "tracelock.focus_zone.default",
        "tracelock.progress_ring.default",
        "tracelock.timer_bar.default",
        "tracelock.effect.trace_seal",
        "tracelock.effect.lock_failed",
        "tracelock.effect.trace_drop",
        "tracelock.effect.combo_popup",
        "audio.ui.click",
        "audio.tracelock.hit",
        "audio.tracelock.miss",
        "font.ui.primary",
    ]
    for key in required:
        assert key in common, key
        assert "url" in common[key]
        assert common[key].get("task25e0_role") or common[key].get("description")


def test_task25e0_pack_declares_handoff_and_slot_groups() -> None:
    pack = _load_json(PACK_ROOT / "pack.json")
    assert pack["asset_handoff"] == "asset_handoff.json"
    assert "asset_directories" in pack
    assert "asset_slot_groups" in pack
    for group in ["backgrounds", "ui", "trace_lock", "effects", "audio", "fonts"]:
        assert group in pack["asset_slot_groups"]


def test_task25e0_trace_lock_json_references_asset_slots_and_keeps_fallbacks() -> None:
    trace_lock = _load_json(PACK_ROOT / "games/trace_lock.json")
    assert trace_lock["canvas"]["asset_key"] == "tracelock.background.grid"
    assert trace_lock["target"]["marked_trace"]["asset_key"] == "tracelock.target.marked_trace"
    assert trace_lock["target"]["marked_trace"]["fallback_shape"] == "circle"
    assert trace_lock["target"]["noise_trace"]["asset_key"] == "tracelock.target.noise_trace"
    assert trace_lock["target"]["noise_trace"]["fallback_shape"] == "diamond"
    assert trace_lock["progress_ring"]["asset_key"] == "tracelock.progress_ring.default"
    assert trace_lock["timer_bar"]["asset_key"] == "tracelock.timer_bar.default"


def test_task25e0_effect_json_references_visual_and_optional_audio_slots() -> None:
    effects = _load_json(PACK_ROOT / "effects/trace_lock_effects.json")
    assert effects["trace_seal"]["asset_key"] == "tracelock.effect.trace_seal"
    assert effects["trace_seal"]["audio_key"] == "audio.tracelock.hit"
    assert effects["lock_failed"]["asset_key"] == "tracelock.effect.lock_failed"
    assert effects["lock_failed"]["audio_key"] == "audio.tracelock.miss"
    assert effects["trace_drop"]["asset_key"] == "tracelock.effect.trace_drop"
    assert effects["combo_popup"]["asset_key"] == "tracelock.effect.combo_popup"


def test_task25e0_asset_handoff_validation_and_bundle_fields() -> None:
    validation = validate_design_pack_asset_handoff()
    assert validation["missing_slots"] == []
    assert validation["invalid_url_assets"] == []
    assert validation["expected_slot_count"] >= 20
    assert validation["null_url_asset_count"] >= 1

    bundle = build_render_resource_bundle("fake_game")
    assert "asset_handoff" in bundle
    assert "asset_handoff_validation" in bundle
    assert bundle["asset_handoff_validation"]["invalid_url_assets"] == []


def test_task25e0_does_not_commit_real_binary_assets_yet() -> None:
    forbidden_exts = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".ttf", ".otf", ".wav", ".ogg", ".mp3"}
    for path in PACK_ROOT.rglob("*"):
        if path.is_file():
            assert path.suffix.lower() not in forbidden_exts, path
