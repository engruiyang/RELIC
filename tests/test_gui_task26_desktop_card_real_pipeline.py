from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_desktop_card_invokes_bridge_without_slot_existence_guard() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "[DESKTOP CARD CLICK]" in text
    assert "[DESKTOP CARD ACTION]" in text
    assert "root.guiBridge.invokeAction(actionId, payloadText)" in text
    assert "!root.guiBridge.invokeAction" not in text
    assert "missing_bridge" in text


def test_desktop_card_has_compact_readable_rows_and_action_feedback() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    for token in [
        "compactLabelPixelSize",
        "compactValuePixelSize",
        "compactButtonHeight",
        "compactWidgetSpacing",
        "lastDesktopActionId",
        "lastDesktopActionStatus",
        "elide: Text.ElideRight",
    ]:
        assert token in text


def test_widget_args_payload_is_exposed_to_qml() -> None:
    model = _read("gui/desktop_model.py")
    preview = _read("ui_qml/components/DesktopLayoutPreview.qml")
    card = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert '"args": w.get("args", {})' in model
    assert '_args_json' in model
    assert "Widget1ArgsJson" in preview
    assert "widget1ArgsJson" in card


def test_active_pages_expose_bridge_and_state_objects_for_card_desktop() -> None:
    pages = [
        "HomePage.qml",
        "TrainingPage.qml",
        "UserPage.qml",
        "CalibrationPage.qml",
        "ReportPage.qml",
        "DiagnosticsPage.qml",
    ]
    for page in pages:
        text = _read(f"ui_qml/pages/{page}")
        assert "property var guiBridge" in text
        assert "property var controlStateObj" in text or "controlStateObj" in text
        assert "Page Commands" in text
        assert "Page Feedback" in text
        assert "guiBridge: typeof guiBridge" not in text

    # Pages that still use DesktopLayoutPreview must pass real state objects.
    for page in pages:
        text = _read(f"ui_qml/pages/{page}")
        if "DesktopLayoutPreview" not in text:
            continue
        assert "guiBridge:" in text
        assert "controlStateObj:" in text
        assert "runtimeSnapshotObj:" in text


def test_minimal_gui_passes_bridge_and_session_to_pages() -> None:
    text = _read("ui_qml/MinimalGui.qml")
    assert "guiBridge: guiBridge" in text
    assert "sessionObj: root.sessionObj" in text
    assert "gameHudObj: root.gameHudObj" in text


def test_gui_bridge_forces_state_refresh_after_invoke_action() -> None:
    text = _read("gui/gui_bridge.py")
    assert "def invokeAction" in text
    assert "self.stateChanged.emit()" in text
    assert "self.controlStateJsonChanged.emit()" in text


def test_report_action_aliases_are_supported_by_facade() -> None:
    text = _read("gui/gui_facade.py")
    assert '"report.latest": "report.refresh"' in text
    assert '"report.list_sessions": "report.list"' in text
    assert '"report.show_session": "report.show"' in text
