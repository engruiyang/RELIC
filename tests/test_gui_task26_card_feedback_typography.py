from pathlib import Path
import json
import importlib.util


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_card_preview_summarizes_action_results_and_keeps_raw_console_output() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "function summarizeActionResult" in text
    assert "extractJsonString" in text
    assert "extractJsonNumber" in text
    assert "root.lastDesktopActionRaw" in text
    assert "console.log(\"[DESKTOP CARD ACTION] action_id=\" + actionId + \" result=\" + raw)" in text
    assert "root.lastDesktopActionMessage = summarizeActionResult(raw, actionId)" in text


def test_card_preview_has_configurable_typography_and_feedback_area() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    for token in [
        "property int titlePixelSize",
        "property int subtitlePixelSize",
        "property int widgetLabelPixelSize",
        "property int widgetValuePixelSize",
        "property int widgetRowHeight",
        "property int buttonHeight",
        "property int feedbackHeight",
        "maximumLineCount: 2",
        "wrapMode: Text.Wrap",
    ]:
        assert token in text


def test_design_card_and_button_accept_typography_values() -> None:
    design = _read("ui_qml/components/DesignCard.qml")
    button = _read("ui_qml/components/ConfigButtonWidget.qml")
    assert "property int titlePixelSize" in design
    assert "font.pixelSize: root.titlePixelSize" in design
    assert "property int subtitlePixelSize" in design
    assert "font.pixelSize: root.subtitlePixelSize" in design
    assert "property int textPixelSize" in button
    assert "font.pixelSize: root.textPixelSize" in button


def test_desktop_model_emits_typography_payload_fields() -> None:
    spec = importlib.util.spec_from_file_location("desktop_model", "gui/desktop_model.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    page = json.loads(Path("assets/layouts/task26_examples/training_page.desktop_demo.json").read_text(encoding="utf-8"))
    payload = module.build_desktop_layout_preview_payload(module.build_page_render_model(page))
    for key in [
        "card1_title_pixel_size",
        "card1_subtitle_pixel_size",
        "card1_widget_label_pixel_size",
        "card1_widget_value_pixel_size",
        "card1_widget_row_height",
        "card1_button_height",
        "card1_feedback_height",
    ]:
        assert key in payload
    module.validate_desktop_layout_preview_payload(payload)


def test_missing_action_buttons_are_declared_in_desktop_json() -> None:
    user = json.loads(Path("assets/layouts/task26_examples/user_page.desktop_demo.json").read_text(encoding="utf-8"))
    calibration = json.loads(Path("assets/layouts/task26_examples/calibration_page.desktop_demo.json").read_text(encoding="utf-8"))
    user_actions = {w.get("action_id") for c in user["cards"] for w in c.get("widgets", [])}
    cal_actions = {w.get("action_id") for c in calibration["cards"] if c["id"] == "calibration_actions_card" for w in c["widgets"]}
    assert "user.create" in user_actions
    assert {"calibration.start", "calibration.show", "calibration.bind"}.issubset(cal_actions)
