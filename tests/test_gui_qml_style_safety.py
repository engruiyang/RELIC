from pathlib import Path
import re


def test_qml_files_are_utf8_and_no_high_risk_inline_button_chains() -> None:
    qml_files = sorted(Path("ui_qml").rglob("*.qml"))
    assert qml_files
    risky = re.compile(r"Button\s*\{[^\n]*\};\s*Button\s*\{")
    for path in qml_files:
        text = path.read_text(encoding="utf-8")
        assert text
        if path.name == "GameCanvas.qml":
            continue
        assert not risky.search(text), f"potential risky inline Button chain in {path}"
