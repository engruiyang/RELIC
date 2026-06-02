from pathlib import Path
import re


def test_task24_training_game_canvas_tokens_present() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    for token in [
        "GameCanvas / Game View",
        "GameCanvas restored in TASK24",
        "GameCanvas will be restored in TASK24",
        "game_canvas_card",
        "No active game view.",
        "entity_count",
        "visual_event_count",
        "pointer_click",
        "guiBridge.sendEvent",
        "TraceLock pipeline",
        "Game Selection",
        "Select Existing Game",
        "Use TraceLock",
        "selected_game_id",
        "game.select",
        "movement_type",
        "target_time_left_ms",
        "accuracy",
        "TASK25 design_pack game_styles active",
        "gameStyleObj",
        "effectStyleObj",
        "DesignMetricCard",
        "trainingGameCanvasLoader",
    ]:
        assert token in text


def test_task24_game_canvas_component_contract() -> None:
    text = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    for token in [
        "property var gameView",
        "property var guiBridgeRef",
        "property string fallbackGameId",
        "MouseArea",
        "pointer_click",
        "sendEvent",
        "entities",
        "property var gameStyleObj",
        "property var effectStyleObj",
        "property var designThemeObj",
        "property var renderResourcesObj",
        "targetGlow",
        "timer_bar",
        "effectColor",
        "DesignBackground",
        "targetAssetKey",
        "targetImageSource",
        "targetFallbackShape",
        "fallback_shape",
        "progressValueFromModel",
        "animationTick",
        "client_created_at_ms",
        "input_phase",
        "Canvas {",
        "backgroundImageSource",
        "isBackgroundImageAvailable",
        "renderResourceStyle",
        "progressStyle",
        "rowImageSource",
        "effectAssetDescriptor",
        "effectImageSource",
        "tracelock.effect.local_ripple",
    ]:
        assert token in text


def test_task26_desktop_card_preview_embeds_live_game_canvas_and_hud_overlay() -> None:
    text = Path("ui_qml/components/DesktopLayoutCardPreview.qml").read_text(encoding="utf-8")
    for token in [
        "function isGameCanvasCard()",
        "desktopGameCanvasLoader",
        "active: root.visible && root.isGameCanvasCard()",
        "sourceComponent: Component",
        "GameCanvas {",
        "diagnosticEnabled: false",
        "HEAD UP DISPLAY",
        "gameHudJson.score",
        "gameHudJson.time_left_ms",
        "runtimeSnapshot.attention",
        "guiBridgeRef: root.guiBridge",
    ]:
        assert token in text


def test_task24_forbidden_patterns_still_blocked_outside_training_page() -> None:
    for qml in Path("ui_qml").rglob("*.qml"):
        if qml.name in {"GameCanvas.qml", "TrainingPage.qml", "DesktopLayoutCardPreview.qml"}:
            continue
        text = qml.read_text(encoding="utf-8")
        for token in ["GameCanvas {", "Loader", "Repeater", "subprocess", "Popen", "os.system"]:
            assert token not in text, f"{token!r} found in {qml}"
        assert re.search(r"interval\s*:\s*100(?!\d)", text) is None, f"'interval: 100' found in {qml}"
