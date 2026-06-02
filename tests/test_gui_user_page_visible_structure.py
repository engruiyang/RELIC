from pathlib import Path


def test_user_page_visible_structure_tokens() -> None:
    qml = Path("ui_qml/pages/UserPage.qml").read_text(encoding="utf-8")
    for token in [
        "User / Profile",
        "Current User Summary",
        "Create / Load User",
        "User List",
        "User Action Result",
        "Profile Detail",
        "Profile Detail Popup",
        "Open Profile Detail Popup",
        "Switch User",
        "selected_user_id",
        "Load Selected User",
        "Show Selected Profile",
        "ComboBox",
        "shouldShowProfileAfterAction",
        "user_id input",
        "display_name input",
        "Load Current",
        "List Users",
        "Show Profile Detail",
        "No users found.",
        "missing_input",
    ]:
        assert token in qml


def test_user_page_uses_native_user_actions_without_forbidden_gui_patterns() -> None:
    qml = Path("ui_qml/pages/UserPage.qml").read_text(encoding="utf-8")
    for action_id in [
        "user.list",
        "user.create",
        "user.load",
        "user.load_current",
        "user.show_profile",
    ]:
        assert action_id in qml
    for forbidden in ["Loader", "Repeater", "subprocess", "interval: 100", "GameCanvas {"]:
        assert forbidden not in qml


def test_gui_bridge_invoke_action_returns_string_to_qml() -> None:
    bridge = Path("gui/gui_bridge.py").read_text(encoding="utf-8")
    assert "@Slot(str, str, result=str)" in bridge
    assert "def invokeAction" in bridge
