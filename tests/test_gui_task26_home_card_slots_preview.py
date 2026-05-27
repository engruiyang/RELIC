from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_home_card_slot_preview_exists() -> None:
    assert Path("ui_qml/components/HomeCardSlotPreview.qml").exists()


def test_home_card_slots_preview_exists() -> None:
    assert Path("ui_qml/components/HomeCardSlotsPreview.qml").exists()


def test_home_card_slot_preview_tokens() -> None:
    text = Path("ui_qml/components/HomeCardSlotPreview.qml").read_text(encoding="utf-8")
    for token in [
        "slotIndex",
        "DesignCard",
        "ConfigTextWidget",
        "cardId",
        "modelX",
        "modelY",
        "modelWidth",
        "modelHeight",
        "actionIdsText",
        "sourceRootsText",
    ]:
        assert token in text


def test_home_card_slots_preview_tokens() -> None:
    text = Path("ui_qml/components/HomeCardSlotsPreview.qml").read_text(encoding="utf-8")
    for token in [
        "Home Card Slots Preview",
        "HomeCardSlotPreview",
        "runtime_io_card",
        "quick_actions_card",
        "recent_session_card",
        "relic_identity_card",
    ]:
        assert token in text


def test_home_slot_components_banned_tokens_absent() -> None:
    for f in ["ui_qml/components/HomeCardSlotPreview.qml", "ui_qml/components/HomeCardSlotsPreview.qml"]:
        text = Path(f).read_text(encoding="utf-8")
        for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest", "JSON.parse", "File", "read"]:
            assert token not in text


def test_developer_lab_contains_slot_preview_tokens() -> None:
    text = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    for token in ["TASK26 Home Card Slots Preview", "HomeCardSlotsPreview", "task26HomeCardSlotsPreview"]:
        assert token in text


def test_developer_lab_keeps_existing_previews() -> None:
    text = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    for token in ["TASK26 Desktop Card Preview", "TASK26 Home Render Model Preview", "CardHostPreview", "HomeRenderModelPreview"]:
        assert token in text


def test_build_tool_generates_slots_json() -> None:
    subprocess.run(["python", "tools/build_task26_render_model.py", "--summary", "--slots"], check=True)
    assert Path("assets/layouts/task26_examples/home_desktop_render_model_slots.example.json").exists()


def test_slots_json_contract() -> None:
    data = json.loads(Path("assets/layouts/task26_examples/home_desktop_render_model_slots.example.json").read_text(encoding="utf-8"))
    assert "slots" in data and isinstance(data["slots"], list)
    assert len(data["slots"]) == 4
    ids = {s.get("card_id") for s in data["slots"]}
    for card_id in ["runtime_io_card", "quick_actions_card", "recent_session_card", "relic_identity_card"]:
        assert card_id in ids
    for s in data["slots"]:
        for k in ["x", "y", "width", "height", "widget_count"]:
            assert k in s
