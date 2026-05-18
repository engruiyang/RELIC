from gui.gui_facade import GuiFacade


def test_user_page_actions_feedback() -> None:
    f = GuiFacade(mode="mock")

    listed = f.invoke_action("user.list", {})
    assert listed.get("status") == "accepted"
    assert "items" in listed
    assert "items_count" in listed

    missing_create = f.invoke_action("user.create", {})
    assert missing_create.get("status") == "missing_input"
    assert missing_create.get("message") == "missing_user_id"

    created = f.invoke_action(
        "user.create",
        {"user_id": "TEST_TASK23B", "display_name": "TASK23B Test User"},
    )
    assert created.get("status") in {"created", "accepted"}
    assert created.get("user_id") == "TEST_TASK23B"
    assert "detail" in created

    missing_load = f.invoke_action("user.load", {})
    assert missing_load.get("status") == "missing_input"

    loaded = f.invoke_action("user.load", {"user_id": "TEST_TASK23B"})
    assert loaded.get("status") == "user_loaded"
    assert loaded.get("user_id") == "TEST_TASK23B"
    assert "detail" in loaded

    current = f.invoke_action("user.load_current", {})
    assert "status" in current

    profile = f.invoke_action("user.show_profile", {})
    assert "status" in profile


def test_user_show_profile_accepts_explicit_user_id_payload() -> None:
    f = GuiFacade(mode="mock")
    f.invoke_action("user.create", {"user_id": "TEST_TASK23B_PAYLOAD", "display_name": "Payload User"})
    profile = f.invoke_action("user.show_profile", {"user_id": "TEST_TASK23B_PAYLOAD"})
    assert profile.get("user_id") == "TEST_TASK23B_PAYLOAD"
    assert "detail" in profile
    assert "profile" in profile
