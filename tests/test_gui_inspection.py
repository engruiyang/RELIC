from __future__ import annotations
import pytest
import json
from pathlib import Path


def test_import_inspect_gui() -> None:
    import ui_cli.inspect_gui as inspect_gui
    assert inspect_gui is not None


def test_report_structure(tmp_path: Path) -> None:
    pytest.importorskip("PySide6")
    from ui_cli import inspect_gui

    out_dir = tmp_path / "gui_inspect"
    args = [
        "--mode", "mock", "--user-id", "TEST", "--db-path", "data/relic_local.db", "--out", str(out_dir), "--no-screenshots"
    ]
    import sys
    old = sys.argv
    sys.argv = ["inspect_gui"] + args
    try:
        inspect_gui.main()
    finally:
        sys.argv = old

    report = json.loads((out_dir / "gui_inspect_report.json").read_text(encoding="utf-8"))
    for page in ["home", "user", "calibration", "training", "report", "diagnostics", "developer_lab"]:
        assert page in report["pages"]
    for panel in ["userSummaryPanel", "userFormPanel", "userListPanel", "userResultPanel"]:
        assert panel in report["pages"]["user"]["panel_geometry"]
    for panel in ["calibrationUserGatePanel", "calibrationBindingPanel", "calibrationListPanel", "calibrationResultPanel"]:
        assert panel in report["pages"]["calibration"]["panel_geometry"]
    for panel in ["reportLatestPanel", "reportListPanel", "reportDetailPanel", "reportResultPanel"]:
        assert panel in report["pages"]["report"]["panel_geometry"]
    assert "trainingGameCanvasPlaceholder" in report["pages"]["training"]["panel_geometry"]
    actions = set()
    for page in report["pages"].values():
        actions.update(page.get("actions", {}).keys())
    for action in ["user.list", "calibration.list", "report.list", "game.status", "devlab.run"]:
        assert action in actions


def test_no_forbidden_patterns() -> None:
    files = [
        Path("ui_cli/inspect_gui.py"),
        *Path("ui_qml/pages").glob("*.qml"),
    ]
    text = "\n".join(f.read_text(encoding="utf-8") for f in files)
    for token in ["Loader", "Repeater", "subprocess", "interval:100"]:
        assert token not in text
    assert "GameCanvas {" not in text
