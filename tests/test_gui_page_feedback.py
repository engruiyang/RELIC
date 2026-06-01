from pathlib import Path
import re


def _has_banned_token(text: str, token: str) -> bool:
    if token == "interval: 100":
        return re.search(r"\binterval\s*:\s*100\b(?!\s*0)", text) is not None
    return token in text


def test_each_page_has_commands_and_feedback_and_no_banned() -> None:
    for p in ["HomePage", "UserPage", "CalibrationPage", "TrainingPage", "ReportPage", "DiagnosticsPage"]:
        text = Path(f"ui_qml/pages/{p}.qml").read_text(encoding="utf-8")
        assert "Page Commands" in text
        assert "Page Feedback" in text

    qml_files = [Path("ui_qml/MinimalGui.qml")] + sorted(Path("ui_qml/pages").glob("*.qml"))
    for path in qml_files:
        text = path.read_text(encoding="utf-8")
        banned = ["subprocess", "Popen", "os.system", "interval: 100"]
        if path.name not in {"TrainingPage.qml"}:
            banned.append("GameCanvas {")
        for token in banned:
            assert not _has_banned_token(text, token), f"{token!r} found in {path}"
