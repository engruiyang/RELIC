from pathlib import Path
import re


def test_qml_files_are_utf8_and_no_inline_object_chain_patterns() -> None:
    qml_files = sorted(Path("ui_qml").rglob("*.qml"))
    assert qml_files

    object_types = [
        "Button", "Label", "Text", "GroupBox", "Rectangle", "Row", "Column",
        "RowLayout", "ColumnLayout", "GridLayout", "ScrollView", "Frame", "Pane",
        "Item", "Page", "StackLayout", "TextArea", "TextField",
    ]
    chain_pattern = re.compile(r"\};\s*(?:" + "|".join(object_types) + r")\s*\{")

    for path in qml_files:
        text = path.read_text(encoding="utf-8")
        assert text
        if path.name == "GameCanvas.qml":
            continue
        assert not chain_pattern.search(text), f"inline object chain risk in {path}"


def test_training_page_first_80_lines_have_no_inline_chain() -> None:
    lines = Path("ui_qml/pages/TrainingPage.qml").read_text(encoding="utf-8").splitlines()
    first_80 = "\n".join(lines[:80])
    banned = [
        "}; Button", "}; Label", "}; Text", "}; GroupBox", "}; Column", "}; Row",
        "}; Rectangle", "}; Item",
    ]
    for token in banned:
        assert token not in first_80
