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


def test_developer_lab_is_focused_algorithm_console_without_legacy_preview_wall() -> None:
    text = _read()
    for token in [
        "Developer Lab is now an algorithm experiment bench.",
        "Runtime Data Panel",
        "Task6B Config Snapshot",
        "FI Grid Search Lab (Experimental)",
        "FI Grid Result",
        "devlab_role_card",
        "devlab_runtime_data_panel",
        "devlab_task6b_config_panel",
        "devlab_fi_grid_panel",
        "devlab_fi_grid_result_panel",
        "devlab_command_summary_panel",
    ]:
        assert token in text
    for old_token in [
        "Developer Lab Actions",
        "runtime.core_debug_mock",
        "runtime.core_debug_live",
        "game.debug_mock",
        "game.debug_live",
        "developer.task6b_record_mock",
        "developer.task6b_record_live",
        "developer.task6b_evaluate",
        "developer.task6b_tune",
        "developer.task6b_calibrate",
        "TASK26 Desktop Card Preview",
        "TASK26 Home Render Model Preview",
        "TASK26 Home Card Slots Preview",
        "TASK26 Training Render Model Preview",
        "TASK26 Training Card Slots Preview",
        "CardHostPreview",
        "HomeRenderModelPreview",
        "TrainingRenderModelPreview",
    ]:
        assert old_token not in text


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


def test_developer_lab_fi_grid_experimental_panel_tokens() -> None:
    text = _read()
    for token in [
        "FI Grid Search Lab (Experimental)",
        "fiGridInputField",
        "fiGridLabelsField",
        "fiGridConfigField",
        "fiGridOutDirField",
        "fiGridStageLimitField",
        "Dry Run Plan",
        "Run Small Grid",
        "devlab.fi_grid_plan",
        "devlab.fi_grid_small_run",
        "reports/devlab",
        "FI Grid Result",
    ]:
        assert token in text
