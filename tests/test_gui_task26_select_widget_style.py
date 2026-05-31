from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_config_select_widget_uses_basic_combobox_and_rounded_popup() -> None:
    text = _read("ui_qml/components/ConfigSelectWidget.qml")
    assert "QtQuick.Controls.Basic" in text
    assert "Basic.ComboBox" in text
    assert "popup: Basic.Popup" in text
    assert "popupCornerRadius" in text
    assert "radius: root.popupCornerRadius" in text
    assert "radius: root.cornerRadius" in text
    assert "popupBackgroundColor" in text
    assert "popupBorderColor" in text


def test_desktop_card_preview_uses_config_select_widget_for_select_widgets() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "ConfigSelectWidget" in text
    assert "Basic.ComboBox" in text
    assert "optionsText: root.widget1OptionsText" in text
    assert "onCurrentTextChanged: root.widget1SelectText = currentText" in text
    assert "ComboBox {" not in text


def test_select_widget_keeps_card_system_forbidden_tokens_out() -> None:
    text = _read("ui_qml/components/ConfigSelectWidget.qml")
    for forbidden in ["eval(", "XMLHttpRequest", "Loader", "Repeater", "Timer", "subprocess"]:
        assert forbidden not in text
