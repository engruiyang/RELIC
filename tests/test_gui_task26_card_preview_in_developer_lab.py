from pathlib import Path


def test_developer_lab_contains_task26_preview_tokens() -> None:
    text = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    assert "CardHostPreview" in text
    assert "TASK26 Desktop Card Preview" in text
    assert "task26CardPreview" in text


def test_developer_lab_does_not_contain_banned_tokens() -> None:
    text = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    for token in ["Loader", "Repeater", "Timer", "subprocess"]:
        assert token not in text


def test_developer_lab_keeps_legacy_tokens() -> None:
    text = Path("ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    assert "Developer Lab" in text
    assert "Page Feedback" in text
    assert "Page Commands" in text


def test_cardhostpreview_keeps_core_tokens() -> None:
    text = Path("ui_qml/components/CardHostPreview.qml").read_text(encoding="utf-8")
    assert "Runtime I/O" in text
    assert "Quick Actions" in text
    assert "live.safe_stop" in text
