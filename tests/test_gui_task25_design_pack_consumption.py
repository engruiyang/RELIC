from pathlib import Path


def test_minimal_gui_passes_design_pack_tokens_to_training_page() -> None:
    text = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    for token in [
        "renderResourcesObj",
        "designThemeObj",
        "pageStylesObj",
        "componentStylesObj",
        "gameStylesObj",
        "effectStylesObj",
        "guiBridge.renderResourcesJson",
        "designThemeObj: root.designThemeObj",
        "pageStyleObj: root.pageStylesObj.training_page",
        "gameStyleObj: root.gameStylesObj.trace_lock",
        "effectStyleObj: root.effectStylesObj.trace_lock",
    ]:
        assert token in text


def test_training_page_consumes_design_pack_without_control_logic_changes() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    for token in [
        "property var renderResourcesObj",
        "property var designThemeObj",
        "property var pageStyleObj",
        "property var componentStyleObj",
        "property var gameStyleObj",
        "property var effectStyleObj",
        "Design Pack Status",
        "themeColor",
        "themeSpacing",
        "gameDesignValue",
        "TASK25 design_pack game_styles active",
    ]:
        assert token in text
    for forbidden in ["subprocess", "Popen", "os.system", "AssetManager", "ThemeManager", "LayoutManager"]:
        assert forbidden not in text


def test_game_canvas_consumes_trace_lock_design_tokens_only_for_rendering() -> None:
    text = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    for token in [
        "property var gameStyleObj",
        "property var effectStyleObj",
        "property var designThemeObj",
        "targetStyle",
        "targetFill",
        "targetStroke",
        "targetGlow",
        "progress_ring",
        "timer_bar",
        "effectColor",
        "visualEvents",
    ]:
        assert token in text
    assert "sendEvent(\"pointer_click\"" in text
    for forbidden in ["subprocess", "Popen", "os.system", "AssetManager", "ThemeManager", "LayoutManager"]:
        assert forbidden not in text
