from __future__ import annotations

import json
from pathlib import Path

import pytest

from gui.desktop_model import (
    build_home_layout_preview_payload,
    build_training_layout_preview_payload,
    validate_desktop_layout_preview_payload,
)
from gui.gui_facade import GuiFacade


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_desktop_layout_preview_components_exist() -> None:
    assert Path("ui_qml/components/DesktopLayoutCardPreview.qml").exists()
    assert Path("ui_qml/components/DesktopLayoutPreview.qml").exists()


def test_desktop_layout_preview_component_tokens() -> None:
    text = _read("ui_qml/components/DesktopLayoutPreview.qml")
    for token in [
        "Desktop Layout Preview",
        "DesktopLayoutCardPreview",
        "modelPageWidth",
        "modelPageHeight",
        "card1X",
        "card1Y",
        "card1Width",
        "card1Height",
        "canvasScale",
    ]:
        assert token in text


def test_developer_lab_contains_home_and_training_layout_previews() -> None:
    text = _read("ui_qml/pages/DeveloperLabPage.qml")
    for token in [
        "TASK26 Home Desktop Layout Preview",
        "TASK26 Training Desktop Layout Preview",
        "DesktopLayoutPreview",
        "task26HomeLayoutPayload",
        "task26HomeLayoutValue",
        "task26TrainingLayoutPayload",
        "task26TrainingLayoutValue",
        "task26_home_layout_payload",
        "task26_training_layout_payload",
    ]:
        assert token in text


def test_layout_preview_qml_avoids_dynamic_file_and_runtime_tokens() -> None:
    for path in [
        "ui_qml/components/DesktopLayoutCardPreview.qml",
        "ui_qml/components/DesktopLayoutPreview.qml",
        "ui_qml/pages/DeveloperLabPage.qml",
    ]:
        text = _read(path)
        for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest"]:
            assert token not in text
        assert "JSON.parse" not in text


def test_home_layout_payload_contains_numeric_rects() -> None:
    payload = build_home_layout_preview_payload(Path("."))
    validate_desktop_layout_preview_payload(payload, max_cards=4)
    assert payload["page_id"] == "home"
    assert payload["card_count"] == 4
    assert payload["card1_id"] == "runtime_io_card"
    for key in ["card1_x", "card1_y", "card1_width", "card1_height"]:
        assert isinstance(payload[key], (int, float))


def test_training_layout_payload_contains_game_canvas_card() -> None:
    payload = build_training_layout_preview_payload(Path("."))
    validate_desktop_layout_preview_payload(payload, max_cards=7)
    ids = {payload[f"card{i}_id"] for i in range(1, 8)}
    assert "game_canvas_card" in ids
    assert payload["page_id"] == "training"


def test_facade_render_resources_contains_layout_payloads() -> None:
    resources = GuiFacade(mode="mock").get_render_resources()
    assert resources["task26_home_layout_status"] == "ok"
    assert resources["task26_training_layout_status"] == "ok"
    validate_desktop_layout_preview_payload(resources["task26_home_layout_payload"], max_cards=4)
    validate_desktop_layout_preview_payload(resources["task26_training_layout_payload"], max_cards=7)


def test_bridge_render_resources_json_contains_layout_payloads() -> None:
    pytest.importorskip("PySide6")
    from gui.gui_bridge import GuiBridge

    bridge = GuiBridge(GuiFacade(mode="mock"))
    data = json.loads(bridge.renderResourcesJson)
    assert data["task26_home_layout_status"] == "ok"
    assert data["task26_training_layout_status"] == "ok"
    assert data["task26_home_layout_payload"]["card1_id"] == "runtime_io_card"
