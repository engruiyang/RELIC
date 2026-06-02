from game.fake_click_game_client import FakeClickGameClient
from game.game_contracts import GameInputEvent


def _evt(x: float, y: float, button: int = 0) -> GameInputEvent:
    return GameInputEvent(
        event_id="evt",
        session_id="s1",
        game_id="fake_click_game",
        input_type="pointer_click",
        created_at_ms=123,
        source="qml",
        x_norm=x,
        y_norm=y,
        button=button,
        raw_event_type="target_click",
        debug_hit=None,
        payload={},
    )


def test_start_sets_zero_score() -> None:
    client = FakeClickGameClient()
    client.start({"session_id": "s1"})
    assert client.get_score() == 0


def test_build_game_view_has_expected_entities() -> None:
    client = FakeClickGameClient()
    client.start({"session_id": "s1"})
    view = client.build_game_view()
    kinds = {entity.kind for entity in view.entities}
    assert "target" in kinds
    assert "focus_zone" in kinds
    assert "progress_ring" in kinds


def test_target_click_event_payload() -> None:
    client = FakeClickGameClient()
    client.start({"session_id": "s1"})
    client.handle_input(_evt(0.5, 0.5, button=0))
    events = client.collect_game_events()
    assert events[0].event_type == "target_click"
    assert events[0].payload["target_index"] == 0
    assert events[0].payload["action_name"] == "target_primary"


def test_background_click_event_payload() -> None:
    client = FakeClickGameClient()
    client.start({"session_id": "s1"})
    client.handle_input(_evt(0.05, 0.05, button=1))
    events = client.collect_game_events()
    assert events[0].event_type == "background_click"
    assert events[0].payload["target_index"] == 1
    assert events[0].payload["action_name"] == "background"


def test_collect_behavior_sample_contains_required_fields() -> None:
    client = FakeClickGameClient()
    client.start({"session_id": "s1"})
    client.handle_input(_evt(0.5, 0.5, button=0))
    sample = client.collect_behavior_sample()
    assert hasattr(sample, "accuracy")
    assert hasattr(sample, "false_action")
    assert hasattr(sample, "rt_stability")


def test_game_view_state_uses_only_keys_not_file_paths() -> None:
    client = FakeClickGameClient()
    client.start({"session_id": "s1"})
    view = client.build_game_view().to_dict()
    entity = view["entities"][0]
    assert "asset_key" in entity and "style_key" in entity
    joined = str(view)
    assert "assets/" not in joined
    assert ".png" not in joined


def test_fake_click_game_client_no_platform_reporter_or_ipc_mouse_data_reference() -> None:
    path = "game/fake_click_game_client.py"
    text = open(path, encoding="utf-8").read()
    assert "PlatformReporter" not in text
    assert "ipc_mouse_data" not in text
