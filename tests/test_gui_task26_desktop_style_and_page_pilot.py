from __future__ import annotations

import json
from pathlib import Path

from gui.desktop_model import (
    build_desktop_layout_preview_payload,
    build_home_render_model,
    build_training_render_model,
    validate_desktop_layout_preview_payload,
)
from gui.gui_facade import GuiFacade


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_layout_payload_carries_visual_style_fields() -> None:
    model = build_home_render_model(Path("."))
    payload = build_desktop_layout_preview_payload(model, max_cards=4)
    validate_desktop_layout_preview_payload(payload, max_cards=4)

    for key in [
        "card1_background_color",
        "card1_background_opacity",
        "card1_border_color",
        "card1_border_width",
        "card1_radius_value",
        "card1_shape_type",
        "card1_background_image",
        "card1_glass_enabled",
        "card1_glass_tint_color",
        "card1_glass_opacity",
        "card1_glass_highlight",
    ]:
        assert key in payload


def test_training_layout_payload_carries_visual_style_fields() -> None:
    model = build_training_render_model(Path("."))
    payload = build_desktop_layout_preview_payload(model, max_cards=7)
    validate_desktop_layout_preview_payload(payload, max_cards=7)
    assert "card7_background_color" in payload
    assert "card7_glass_enabled" in payload


def test_facade_exposes_style_capable_layout_payloads() -> None:
    resources = GuiFacade(mode="mock").get_render_resources()
    assert resources["task26_home_layout_status"] == "ok"
    assert resources["task26_training_layout_status"] == "ok"
    home_payload = resources["task26_home_layout_payload"]
    training_payload = resources["task26_training_layout_payload"]
    assert "card1_background_color" in home_payload
    assert "card1_glass_enabled" in home_payload
    assert "card1_background_color" in training_payload
    assert "card7_glass_enabled" in training_payload


def test_desktop_layout_preview_components_support_visual_style_tokens() -> None:
    preview = _read("ui_qml/components/DesktopLayoutPreview.qml")
    card = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    design = _read("ui_qml/components/DesignCard.qml")

    for token in [
        "layoutPayload",
        "card1BackgroundColor",
        "card1GlassEnabled",
        "card7GlassHighlight",
    ]:
        assert token in preview

    for token in [
        "cardBackgroundColor",
        "cardBackgroundOpacity",
        "cardBorderColor",
        "cardBorderWidth",
        "cardRadiusValue",
        "cardShapeType",
        "cardBackgroundImage",
        "cardGlassEnabled",
        "cardGlassTintColor",
        "cardGlassOpacity",
        "cardGlassHighlight",
    ]:
        assert token in card

    for token in [
        "glassEnabled",
        "glassTintColor",
        "glassOpacity",
        "glassHighlight",
        "glassTintLayer",
        "glassTopHighlight",
        "effectiveRadius",
    ]:
        assert token in design


def test_home_and_training_pages_use_desktop_layout_pilot_without_slots_payload() -> None:
    home = _read("ui_qml/pages/HomePage.qml")
    training = _read("ui_qml/pages/TrainingPage.qml")

    for token in [
        "TASK26 Home Desktop Pilot",
        "DesktopLayoutPreview",
        "task26HomeLayoutPayload",
        "task26_home_layout_payload",
        "task26DesktopPilotEnabled",
        "task26LegacyFallbackVisible",
    ]:
        assert token in home

    for token in [
        "TASK26 Training Desktop Pilot",
        "DesktopLayoutPreview",
        "task26TrainingLayoutPayload",
        "task26_training_layout_payload",
        "task26DesktopPilotEnabled",
        "task26LegacyFallbackVisible",
        "game_canvas_card",
    ]:
        assert token in training

    for token in [
        "task26_home_slots_payload",
        "task26_training_slots_payload",
        "HomeCardSlotsPreview",
        "TrainingCardSlotsPreview",
    ]:
        assert token not in home
        assert token not in training


def test_legacy_page_tokens_are_kept_for_fallback() -> None:
    home = _read("ui_qml/pages/HomePage.qml")
    training = _read("ui_qml/pages/TrainingPage.qml")

    for token in ["State Summary", "Action Panel", "Page Commands"]:
        assert token in home

    for token in [
        "Training Page",
        "Training Page Actions",
        "Start Session",
        "Stop Session",
        "GameCanvas will be restored in TASK24",
        "GameCanvas restored in TASK24",
        "GameCanvas {",
        "Use TraceLock",
    ]:
        assert token in training


def test_desktop_style_demo_json_contains_visible_style_examples() -> None:
    home = json.loads(Path("assets/layouts/task26_examples/home_page.desktop_demo.json").read_text(encoding="utf-8"))
    training = json.loads(Path("assets/layouts/task26_examples/training_page.desktop_demo.json").read_text(encoding="utf-8"))

    for data in [home, training]:
        assert data["cards"]
        first_style = data["cards"][0].get("style") or {}
        for token in ["background_color", "background_opacity", "border_color", "border_width", "corner_radius", "glass_enabled"]:
            assert token in first_style


def test_new_desktop_style_qml_avoids_banned_dynamic_tokens() -> None:
    for path in [
        "ui_qml/components/DesktopLayoutPreview.qml",
        "ui_qml/components/DesktopLayoutCardPreview.qml",
        "ui_qml/components/DesignCard.qml",
    ]:
        text = _read(path)
        for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest", "JSON.parse"]:
            assert token not in text
