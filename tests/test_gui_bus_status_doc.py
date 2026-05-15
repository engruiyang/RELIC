from pathlib import Path


def test_gui_bus_status_doc_contains_boundary_contract() -> None:
    doc = Path("docs/gui_bus_status.md")
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")

    for token in [
        "RuntimeSnapshot",
        "GuiBridge",
        "GameInputEvent",
        "GameViewState",
        "GameEvent",
        "BehaviorSample",
        "QML 不判断命中",
        "QML 不生成 GameEvent",
        "TASK23",
        "TASK24",
        "TASK25",
    ]:
        assert token in text
