from __future__ import annotations

import json
from pathlib import Path

from core.resource_managers import build_render_resource_bundle


PACK_ROOT = Path("assets/packs/default")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_default_pack_files_exist() -> None:
    required = [
        PACK_ROOT / "pack.json",
        PACK_ROOT / "theme.json",
        PACK_ROOT / "components/button.json",
        PACK_ROOT / "components/panel.json",
        PACK_ROOT / "games/trace_lock.json",
        PACK_ROOT / "effects/trace_lock_effects.json",
    ]
    for path in required:
        assert path.exists(), f"missing: {path}"


def test_pack_json_contract_fields() -> None:
    pack = _load_json(PACK_ROOT / "pack.json")
    required = ["pack_id", "display_name", "version", "theme", "pages", "components", "games", "effects", "fallback_pack"]
    for field in required:
        assert field in pack


def test_theme_button_panel_trace_lock_and_effects_required_fields() -> None:
    theme = _load_json(PACK_ROOT / "theme.json")
    button = _load_json(PACK_ROOT / "components/button.json")
    panel = _load_json(PACK_ROOT / "components/panel.json")
    trace_lock = _load_json(PACK_ROOT / "games/trace_lock.json")
    effects = _load_json(PACK_ROOT / "effects/trace_lock_effects.json")

    assert set(["background", "panel", "panel_border", "text", "accent"]).issubset(theme["colors"])
    assert set(["font_family", "title_size", "body_size"]).issubset(theme["typography"])
    assert set(["page_margin", "section_gap"]).issubset(theme["spacing"])

    for state in ["normal", "pressed", "disabled"]:
        assert set(["background", "border", "text"]).issubset(button[state])
    assert set(["radius", "padding_x", "padding_y"]).issubset(button)

    assert set(["background", "border", "radius", "padding", "shadow_enabled", "opacity"]).issubset(panel)

    assert trace_lock["game_id"] == "trace_lock"
    assert "background" in trace_lock["canvas"]
    assert set(["fill", "stroke", "glow"]).issubset(trace_lock["target"]["marked_trace"])
    assert "fill" in trace_lock["target"]["noise_trace"]
    assert set(["stroke", "background"]).issubset(trace_lock["progress_ring"])
    assert set(["fill", "background"]).issubset(trace_lock["timer_bar"])
    assert set(["position", "text_color"]).issubset(trace_lock["hud"])

    assert set(["type", "duration_ms", "particle_count", "color"]).issubset(effects["trace_seal"])
    assert set(["type", "duration_ms", "color"]).issubset(effects["lock_failed"])
    assert set(["type", "duration_ms"]).issubset(effects["trace_drop"])
    assert "duration_ms" in effects["combo_popup"]


def test_build_render_resource_bundle_includes_new_and_legacy_fields() -> None:
    bundle = build_render_resource_bundle("fake_game")
    for field in ["theme_id", "layout_id", "game_id", "assets", "styles", "layout_regions", "missing_assets", "missing_styles", "missing_regions"]:
        assert field in bundle
    for field in ["design_pack", "theme", "page_styles", "component_styles", "game_styles", "effect_styles", "missing_design_pack_fields"]:
        assert field in bundle


def test_no_binary_art_assets_in_repo() -> None:
    forbidden_exts = {".png", ".jpg", ".jpeg", ".svg", ".ttf", ".otf", ".wav", ".mp3"}
    for path in PACK_ROOT.rglob("*"):
        assert path.suffix.lower() not in forbidden_exts
