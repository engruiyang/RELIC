from pathlib import Path


def test_game_integration_guide_exists_and_has_required_sections() -> None:
    p = Path("docs/game_integration_guide.md")
    assert p.exists()
    t = p.read_text(encoding="utf-8")
    for token in [
        "GameInputEvent", "GameClient", "GameViewState", "GameEvent", "BehaviorSample", "RuntimeSnapshotView",
        "TraceLock", "minimal_game_template", "fake_click", "QML 只传输入事实", "TASK23", "TASK24", "不恢复 GameCanvas",
    ]:
        assert token in t
