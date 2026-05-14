from __future__ import annotations

import json
from pathlib import Path

from core.resource_managers import AssetManager, LayoutManager, ThemeManager, build_render_resource_bundle


def test_asset_manager_manifest_and_visual_load():
    am = AssetManager("assets")
    assert am.manifest["schema_version"] == "asset_manifest.v1"
    vm = am.load_game_visual_manifest("fake_game")
    assert vm.game_id == "fake_game"
    assert "fake_game.target.primary" in vm.assets


def test_asset_resolve_and_missing_fallback():
    am = AssetManager("assets")
    hit = am.resolve_asset("fake_game", "fake_game.target.primary")
    assert hit["exists"] is True
    assert hit["asset_key"] == "fake_game.target.primary"
    miss = am.resolve_asset("fake_game", "fake_game.missing")
    assert miss["exists"] is False
    assert miss["fallback_shape"] == "circle"


def test_theme_manager_style_and_fallback():
    tm = ThemeManager("assets", "default")
    assert tm.theme_id == "default"
    style = tm.resolve_style("target.primary")
    assert style["exists"] is True
    missing = tm.resolve_style("target.not_exists")
    assert missing["exists"] is False
    assert missing["source"] in {"theme.styles.fallback", "missing"}


def test_layout_manager_regions_and_not_game_position_logic():
    lm = LayoutManager("assets", "minimal_gui")
    region = lm.resolve_region("game_canvas")
    assert region["exists"] is True
    assert "target" not in (lm.layout.get("regions") or {})


def test_bundle_json_and_required_fields():
    bundle = build_render_resource_bundle("fake_game")
    encoded = json.dumps(bundle)
    assert encoded
    assert "assets" in bundle and "styles" in bundle and "layout_regions" in bundle
    dump = json.dumps(bundle)
    for forbidden in ["ipc_mouse_data", "PlatformReporter", "SessionManager", "SQLite", "DataCenter", "GameEvent", "GameInputEvent", "FI", "SQI"]:
        assert forbidden not in dump


def test_boundary_pollution_checks():
    vm_text = Path("assets/games/fake_game/visual_manifest.json").read_text(encoding="utf-8")
    theme_text = Path("assets/themes/default/theme.json").read_text(encoding="utf-8")
    layout_text = Path("assets/layouts/minimal_gui.json").read_text(encoding="utf-8")
    for forbidden in ["ipc_mouse_data", "PlatformReporter", "SessionManager"]:
        assert forbidden not in vm_text
    for forbidden in ["hit", "score", "FI", "SQI"]:
        assert forbidden not in theme_text
        assert forbidden not in layout_text


def test_game_sources_do_not_import_resource_managers_or_real_paths():
    fake_game = Path("game/fake_click_game_client.py").read_text(encoding="utf-8")
    minimal_game = Path("game/templates/minimal_game/minimal_game_client.py").read_text(encoding="utf-8")
    for needle in ["AssetManager", "ThemeManager", "LayoutManager"]:
        assert needle not in fake_game
        assert needle not in minimal_game
    for needle in ["assets/", ".png"]:
        assert needle not in fake_game
        assert needle not in minimal_game


def test_visual_manifest_url_change_not_affect_client_logic(tmp_path: Path):
    vm_path = Path("assets/games/fake_game/visual_manifest.json")
    data = json.loads(vm_path.read_text(encoding="utf-8"))
    data["assets"]["fake_game.target.primary"]["url"] = "images/new_target.png"
    p = tmp_path / "assets"
    (p / "games/fake_game").mkdir(parents=True)
    (p / "themes/default").mkdir(parents=True)
    (p / "layouts").mkdir(parents=True)
    (p / "manifest.json").write_text(Path("assets/manifest.json").read_text(encoding="utf-8"), encoding="utf-8")
    (p / "themes/default/theme.json").write_text(Path("assets/themes/default/theme.json").read_text(encoding="utf-8"), encoding="utf-8")
    (p / "layouts/minimal_gui.json").write_text(Path("assets/layouts/minimal_gui.json").read_text(encoding="utf-8"), encoding="utf-8")
    (p / "games/fake_game/visual_manifest.json").write_text(json.dumps(data), encoding="utf-8")
    am = AssetManager(str(p))
    hit = am.resolve_asset("fake_game", "fake_game.target.primary")
    assert hit["url"] == "images/new_target.png"
