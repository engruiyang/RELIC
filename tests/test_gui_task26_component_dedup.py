from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_common_component_files_exist() -> None:
    for path in [
        "ui_qml/components/DesktopCardSlotPreview.qml",
        "ui_qml/components/RenderModelSummaryPreview.qml",
        "ui_qml/components/HomeCardSlotPreview.qml",
        "ui_qml/components/TrainingCardSlotPreview.qml",
        "ui_qml/components/HomeRenderModelPreview.qml",
        "ui_qml/components/TrainingRenderModelPreview.qml",
    ]:
        assert Path(path).exists()


def test_slot_preview_wrappers_use_common_component() -> None:
    home = _read("ui_qml/components/HomeCardSlotPreview.qml")
    training = _read("ui_qml/components/TrainingCardSlotPreview.qml")
    assert "DesktopCardSlotPreview" in home
    assert "DesktopCardSlotPreview" in training
    assert "modelX" in home and "modelWidth" in home
    assert "placeholder" in training and "roleText" in training


def test_render_model_wrappers_use_common_component() -> None:
    home = _read("ui_qml/components/HomeRenderModelPreview.qml")
    training = _read("ui_qml/components/TrainingRenderModelPreview.qml")
    assert "RenderModelSummaryPreview" in home
    assert "RenderModelSummaryPreview" in training
    assert "Home Render Model Preview" in home
    assert "Training Render Model Preview" in training


def test_common_components_keep_expected_visual_primitives() -> None:
    slot = _read("ui_qml/components/DesktopCardSlotPreview.qml")
    summary = _read("ui_qml/components/RenderModelSummaryPreview.qml")
    for token in ["DesignCard", "ConfigTextWidget"]:
        assert token in slot
        assert token in summary


def test_component_dedup_does_not_add_banned_dynamic_tokens() -> None:
    for path in [
        "ui_qml/components/DesktopCardSlotPreview.qml",
        "ui_qml/components/RenderModelSummaryPreview.qml",
        "ui_qml/components/HomeCardSlotPreview.qml",
        "ui_qml/components/TrainingCardSlotPreview.qml",
        "ui_qml/components/HomeRenderModelPreview.qml",
        "ui_qml/components/TrainingRenderModelPreview.qml",
    ]:
        text = _read(path)
        for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest"]:
            assert token not in text
        assert "JSON.parse" not in text


def test_component_audit_document_records_no_immediate_deletion() -> None:
    text = _read("docs/gui/TASK26_component_dedup_audit.md")
    assert "No component should be physically deleted in this patch." in text
    assert "mandatory I/O/safety modules are cardified but cannot disappear" in text
