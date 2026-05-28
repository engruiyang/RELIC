from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_training_render_model_preview_component_exists_and_has_contract_tokens() -> None:
    path = Path("ui_qml/components/TrainingRenderModelPreview.qml")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for token in [
        "Training Render Model Preview",
        "TASK26F-1 bridge summary preview",
        "DesignCard",
        "ConfigTextWidget",
        "pageId",
        "cardCount",
        "widgetCount",
        "requiredCardsText",
        "actionsText",
        "sourceRootsText",
        "placeholderSourcesText",
        "gameCanvasStatusText",
        "safeStopPresent",
    ]:
        assert token in text


def test_developer_lab_contains_training_summary_preview() -> None:
    text = _read("ui_qml/pages/DeveloperLabPage.qml")
    for token in [
        "TASK26 Training Render Model Preview",
        "TrainingRenderModelPreview",
        "task26TrainingRenderModelPreview",
        "task26TrainingValue",
        "task26TrainingListValue",
        "task26_training_summary",
    ]:
        assert token in text


def test_home_and_training_pages_do_not_consume_training_summary_preview() -> None:
    for path in ["ui_qml/pages/HomePage.qml", "ui_qml/pages/TrainingPage.qml"]:
        text = _read(path)
        for token in ["task26_training_summary", "TrainingRenderModelPreview", "task26TrainingValue"]:
            assert token not in text


def test_training_preview_qml_avoids_dynamic_file_and_runtime_tokens() -> None:
    for path in ["ui_qml/components/TrainingRenderModelPreview.qml", "ui_qml/pages/DeveloperLabPage.qml"]:
        text = _read(path)
        for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest", "File", "read"]:
            assert token not in text
        assert "JSON.parse" not in text
