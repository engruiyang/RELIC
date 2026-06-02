from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_home_render_model_preview_component_exists_and_tokens() -> None:
    path = Path("ui_qml/components/HomeRenderModelPreview.qml")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for token in [
        "Home Render Model Preview",
        "TASK26E-1 summary-only preview",
        "DesignCard",
        "ConfigTextWidget",
        "pageId",
        "cardCount",
        "widgetCount",
        "requiredCardCount",
        "lockedCardCount",
        "actionsText",
        "sourceRootsText",
        "cardIdsText",
    ]:
        assert token in text


def test_home_render_model_preview_no_banned_tokens() -> None:
    text = Path("ui_qml/components/HomeRenderModelPreview.qml").read_text(encoding="utf-8")
    for token in ["Loader", "Repeater", "Timer", "subprocess", "XMLHttpRequest", "File", "read", "JSON.parse"]:
        assert token not in text


def test_developer_lab_contains_home_render_model_preview_tokens() -> None:
    text = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    for token in ["TASK26 Home Render Model Preview", "HomeRenderModelPreview", "task26HomeRenderModelPreview"]:
        assert token in text


def test_developer_lab_keeps_existing_task26_preview() -> None:
    text = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    for token in ["TASK26 Desktop Card Preview", "CardHostPreview", "task26CardPreview"]:
        assert token in text


def test_developer_lab_no_banned_tokens() -> None:
    text = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    for token in ["Loader", "Repeater", "Timer", "subprocess"]:
        assert token not in text


def test_build_tool_summary_generates_file() -> None:
    subprocess.run(["python", "tools/build_task26_render_model.py", "--summary"], check=True)
    summary_path = Path("assets/layouts/task26_examples/home_desktop_render_model_summary.example.json")
    assert summary_path.exists()


def test_summary_json_contract() -> None:
    summary_path = Path("assets/layouts/task26_examples/home_desktop_render_model_summary.example.json")
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    for key in ["page_id", "card_count", "widget_count", "action_ids", "source_roots", "card_ids", "preview_lines"]:
        assert key in data
    assert "live.safe_stop" in data["action_ids"] or "app.refresh_now" in data["action_ids"]
    assert "runtime_io_card" in data["card_ids"]
    assert "quick_actions_card" in data["card_ids"]
