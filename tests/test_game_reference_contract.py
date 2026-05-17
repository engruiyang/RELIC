from pathlib import Path


def test_reference_clients_do_not_import_forbidden_modules() -> None:
    files = [
        "game/examples/trace_lock/trace_lock_client.py",
        "game/templates/minimal_game/minimal_game_client.py",
        "game/fake_click_game_client.py",
    ]
    forbidden = ["device", "data", "storage", "calibration", "session", "platform"]
    for fp in files:
        text = Path(fp).read_text(encoding="utf-8")
        for mod in forbidden:
            assert f"import {mod}\n" not in text
            assert f"from {mod} " not in text


def test_game_contract_has_json_serializable_views_and_behavior_fields() -> None:
    text = Path("game/game_contracts.py").read_text(encoding="utf-8")
    for token in ["class GameViewState", "json.dumps(data)", "class BehaviorSample", "action_count", "accuracy", "omission", "false_action", "rt_stability"]:
        assert token in text
