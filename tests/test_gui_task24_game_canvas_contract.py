from pathlib import Path


def test_task24_training_game_canvas_tokens_present() -> None:
    text = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8")
    for token in [
        "GameCanvas / Game View",
        "GameCanvas restored in TASK24",
        "GameCanvas will be restored in TASK24",
        "No active game view.",
        "entity_count",
        "visual_event_count",
        "pointer_click",
        "guiBridge.sendEvent",
        "TraceLock pipeline",
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
    ]:
        assert token in text


def test_task24_forbidden_patterns_still_blocked_outside_training_page() -> None:
    for qml in Path("ui_qml").rglob("*.qml"):
        if qml.name in {"GameCanvas.qml", "TrainingPage.qml"}:
            continue
        text = qml.read_text(encoding="utf-8")
        for token in ["GameCanvas {", "Loader", "Repeater", "interval: 100", "subprocess", "Popen", "os.system"]:
            assert token not in text, f"{token!r} found in {qml}"
