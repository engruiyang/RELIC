from pathlib import Path


def test_minimal_gui_global_skin_layer_consumes_design_pack_tokens() -> None:
    text = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    for token in [
        "renderResourcesObj",
        "designThemeObj",
        "pageStylesObj",
        "componentStylesObj",
        "gameStylesObj",
        "effectStylesObj",
        "guiBridge.renderResourcesJson",
        "DesignBackground",
        "DesignPanel",
        "DesignButton",
        "pageStyle(\"app_shell\")",
        "componentStyle(\"button\")",
        "componentStyle(\"panel\")",
        "TASK25B global GUI skin layer",
        "background.app.main",
    ]:
        assert token in text


def test_training_page_consumes_page_theme_and_hud_design_pack_without_control_logic_changes() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    for token in [
        "property var renderResourcesObj",
        "property var designThemeObj",
        "property var pageStyleObj",
        "property var componentStyleObj",
        "property var gameStyleObj",
        "property var effectStyleObj",
        "DesignBackground",
        "Design Pack Status",
        "themeColor",
        "themeSpacing",
        "gameDesignValue",
        "gameHudCardStyle",
        "DesignMetricCard",
        "TASK25B enlarged design-pack HUD metric cards active",
        "TASK25 design_pack game_styles active",
    ]:
        assert token in text
    for forbidden in ["subprocess", "Popen", "os.system", "AssetManager", "ThemeManager", "LayoutManager"]:
        assert forbidden not in text


def test_game_canvas_consumes_trace_lock_design_tokens_and_background_layers_only_for_rendering() -> None:
    text = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    for token in [
        "property var gameStyleObj",
        "property var effectStyleObj",
        "property var designThemeObj",
        "property var renderResourcesObj",
        "DesignBackground",
        "targetStyle",
        "targetFill",
        "targetStroke",
        "targetGlow",
        "progress_ring",
        "timer_bar",
        "effectColor",
        "visualEvents",
        "canvas.background layered color/image/gradient/overlay",
    ]:
        assert token in text
    assert "sendEvent(\"pointer_click\"" in text
    for forbidden in ["subprocess", "Popen", "os.system", "AssetManager", "ThemeManager", "LayoutManager"]:
        assert forbidden not in text


def test_design_components_exist_and_do_not_use_native_button_background_customization() -> None:
    for rel in [
        "ui_qml/components/DesignBackground.qml",
        "ui_qml/components/DesignPanel.qml",
        "ui_qml/components/DesignButton.qml",
        "ui_qml/components/DesignMetricCard.qml",
    ]:
        assert Path(rel).exists(), rel
    button = Path("ui_qml/components/DesignButton.qml").read_text(encoding="utf-8")
    assert "MouseArea" in button
    assert "background: Rectangle" not in button
    assert "native Button background" in button


def test_design_pack_background_contract_supports_images_and_fallbacks() -> None:
    for rel in [
        "assets/packs/default/theme.json",
        "assets/packs/default/pages/app_shell.json",
        "assets/packs/default/pages/training_page.json",
        "assets/packs/default/games/trace_lock.json",
    ]:
        text = Path(rel).read_text(encoding="utf-8")
        assert "layered" in text
        assert "asset_key" in text
        assert "fit" in text
        assert "opacity" in text
    manifest = Path("assets/manifest.json").read_text(encoding="utf-8")
    for token in ["background.app.main", "background.training.main", "tracelock.background.grid"]:
        assert token in manifest
