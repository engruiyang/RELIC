import json
from pathlib import Path

from gui.desktop_coverage import validate_action_ids
from gui.desktop_schema import collect_action_ids_from_obj
from gui.desktop_model import build_training_layout_preview_payload


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_card_preview_invokes_existing_gui_bridge_action_method() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "function invokeDesktopAction" in text
    assert "guiBridge.invokeAction(actionId" in text
    assert "onActionRequested" in text
    assert "invokeDesktopAction(actionId)" in text


def test_safe_stop_action_is_renderable_from_training_payload() -> None:
    payload = build_training_layout_preview_payload(Path("."))
    actions = {
        payload[f"card{card_idx}_widget{widget_idx}_action_id"]
        for card_idx in range(1, 8)
        for widget_idx in range(1, 7)
    }
    assert "live.safe_stop" in actions


def test_desktop_card_pipeline_does_not_add_unknown_action_ids() -> None:
    action_ids = set()
    for path in Path("assets/layouts/task26_examples").glob("*.desktop_demo.json"):
        action_ids |= collect_action_ids_from_obj(json.loads(path.read_text(encoding="utf-8")))
    validate_action_ids(action_ids)
