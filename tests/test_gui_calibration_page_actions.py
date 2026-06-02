from gui.gui_facade import GuiFacade


def test_calibration_actions_have_status_and_result() -> None:
    f = GuiFacade(mode="mock")
    for action in [
        "calibration.status",
        "calibration.list",
        "calibration.latest",
        "calibration.show",
        "calibration.bind",
        "calibration.cancel",
        "calibration.start",
    ]:
        payload = {"user_id": "TEST"}
        if action in {"calibration.show", "calibration.bind"}:
            payload["calibration_id"] = ""
        result = f.invoke_action(action, payload)
        assert isinstance(result, dict)
        assert "status" in result
        assert "result" in result


def test_calibration_missing_inputs_are_visible() -> None:
    f = GuiFacade(mode="mock")
    assert f.invoke_action("calibration.list", {"user_id": ""}).get("status") == "missing_user"
    assert f.invoke_action("calibration.show", {"user_id": "TEST"}).get("status") == "missing_input"
    assert f.invoke_action("calibration.bind", {"user_id": "TEST"}).get("status") == "missing_input"


def test_calibration_list_shape_for_current_user() -> None:
    f = GuiFacade(mode="mock")
    result = f.invoke_action("calibration.list", {"user_id": "TEST"})
    assert result.get("status") == "accepted"
    assert "items" in result
    assert "items_count" in result


def test_calibration_start_exposes_progress_guidance() -> None:
    f = GuiFacade(mode="mock")
    result = f.invoke_action("calibration.start", {"user_id": "TEST"})
    assert result.get("status") == "start_guidance"
    assert result.get("result") == "calibration_progress"
    progress = result.get("progress") or {}
    assert progress.get("phase_prompts")
    assert "phase_prompt_text" in progress
    assert "佩戴检查" in str(progress.get("phase_prompt_text"))
    assert "注意力基线检查" in str(progress.get("phase_prompt_text"))
    assert "output_tail" in progress
    assert "output_text" in progress

    polled = f.invoke_action("calibration.poll", {})
    assert polled.get("result") == "calibration_progress"
    assert "progress" in polled
