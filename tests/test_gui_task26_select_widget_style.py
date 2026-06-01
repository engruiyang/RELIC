from pathlib import Path


def test_desktop_card_preview_uses_config_select_widget_for_select_widgets() -> None:
    text = Path("ui_qml/components/DesktopLayoutCardPreview.qml").read_text(encoding="utf-8")
    assert "ConfigSelectWidget" in text
    assert "optionsText:" in text
    assert "widget1OptionsText" in text
    assert "widget6OptionsText" in text
    assert "reportSelectorOptionsText" in text
