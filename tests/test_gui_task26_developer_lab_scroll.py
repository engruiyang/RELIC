from pathlib import Path


DEVLAB = Path("ui_qml/pages/DeveloperLabPage.qml")


def _read() -> str:
    return DEVLAB.read_text(encoding="utf-8")


def test_developer_lab_page_has_vertical_scroll_container() -> None:
    text = _read()
    for token in [
        "Flickable",
        "developerLabScroll",
        "developerLabContent",
        "ScrollBar.vertical",
        "contentHeight: developerLabContent.implicitHeight",
        "clip: true",
        "boundsBehavior: Flickable.StopAtBounds",
    ]:
        assert token in text


def test_developer_lab_scroll_keeps_task26_preview_sections() -> None:
    text = _read()
    for token in [
        "TASK26 Desktop Card Preview",
        "TASK26 Home Render Model Preview",
        "TASK26 Home Card Slots Preview",
        "TASK26 Training Render Model Preview",
        "TASK26 Training Card Slots Preview",
    ]:
        assert token in text


def test_developer_lab_feedback_bindings_do_not_depend_on_parent_after_scroll_wrap() -> None:
    text = _read()
    for token in [
        "selectedCommandId: root.selectedCommandId",
        "selectedStatus: root.selectedStatus",
        "selectedExecutionMode: root.selectedExecutionMode",
        "selectedNativeActionId: root.selectedNativeActionId",
    ]:
        assert token in text
    for token in [
        "selectedCommandId: parent.selectedCommandId",
        "selectedStatus: parent.selectedStatus",
        "selectedExecutionMode: parent.selectedExecutionMode",
        "selectedNativeActionId: parent.selectedNativeActionId",
    ]:
        assert token not in text


def test_developer_lab_scroll_does_not_add_banned_runtime_tokens() -> None:
    text = _read()
    for token in [
        "Loader",
        "Repeater",
        "Timer",
        "subprocess",
        "XMLHttpRequest",
    ]:
        assert token not in text
