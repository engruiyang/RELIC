import json
from pathlib import Path

import pytest

from gui.gui_facade import GuiFacade

PySide6 = pytest.importorskip("PySide6")

from gui.gui_bridge import GuiBridge


@pytest.mark.parametrize("mode", ["mock", "core", "core-control", "live-readonly", "live-control"])
def test_gui_facade_modes_have_render_resources(mode: str, tmp_path) -> None:
    kwargs = {"mode": mode}
    if mode in {"core", "core-control"}:
        kwargs["db_path"] = str(tmp_path / "relic.db")
    facade = GuiFacade(**kwargs)
    bundle = facade.get_render_resources()
    assert bundle["theme_id"] == "default"
    assert bundle["layout_id"] == "minimal_gui"
    assert bundle["game_id"] == "fake_game"
    assert "assets" in bundle
    assert "styles" in bundle
    assert "layout_regions" in bundle
    assert "design_pack" in bundle
    assert "theme" in bundle
    assert "page_styles" in bundle
    assert "component_styles" in bundle
    assert "game_styles" in bundle
    assert "effect_styles" in bundle
    assert "background.app.main" in bundle["assets"]
    json.dumps(bundle)
    facade.close()


def test_gui_bridge_render_resources_json_fields() -> None:
    facade = GuiFacade(mode="mock")
    bridge = GuiBridge(facade)
    payload = json.loads(bridge.renderResourcesJson)
    assert "fake_game.target.primary" in payload["assets"]
    assert "target.primary" in payload["styles"]
    assert "game_canvas" in payload["layout_regions"]
    assert payload["design_pack"].get("pack_id") == "default"
    assert "app_shell" in payload["page_styles"]
    assert "button" in payload["component_styles"]
    assert "trace_lock" in payload["game_styles"]


def test_game_client_sources_do_not_import_resource_managers() -> None:
    for path in Path("game").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "AssetManager" not in text
        assert "ThemeManager" not in text
        assert "LayoutManager" not in text


def test_qml_does_not_directly_read_assets_json_or_platform_paths() -> None:
    text = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    assert "assets/" not in text
    assert ".json" not in text or "renderResourcesJson" in text
    assert "PlatformReporter" not in text
    assert "ipc_mouse_data" not in text
