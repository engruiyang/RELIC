import json

from game.game_contracts import BehaviorSample, GameEntity, GameEvent, GameInputEvent, GameViewState, VisualEvent


def test_game_input_event_serializable() -> None:
    evt = GameInputEvent(
        event_id="e1",
        session_id="s1",
        game_id="g1",
        input_type="pointer_click",
        created_at_ms=1,
        source="qml",
        x_norm=0.5,
        y_norm=0.5,
        button=0,
        raw_event_type="target_click",
        debug_hit=True,
        payload={"k": "v"},
    )
    json.dumps(evt.to_dict())


def test_game_event_serializable() -> None:
    evt = GameEvent("game_event.v1", "e1", "s1", "g1", "target_click", 2, True, {"hit": True})
    json.dumps(evt.to_dict())


def test_game_view_state_serializable() -> None:
    view = GameViewState(
        game_id="g1",
        view_version="game_view.v1",
        frame_id=1,
        score=2,
        combo=1,
        level=1,
        hud={"score": 2},
        entities=[GameEntity("id", "target", "primary", 0.5, 0.5, 0.1, "active", "style", "asset", True, "circle")],
        visual_events=[VisualEvent("v1", "pulse", "id", 0.5, 0.5, "eff", "style", 1.0, 100)],
        layout_hints={"theme": "default"},
    )
    json.dumps(view.to_dict())


def test_behavior_sample_serializable() -> None:
    sample = BehaviorSample(1000, 10, 8, 2, 1, 9, [200, 210], 0.8, 0.2, 0.1, 0.9, {"k": "v"})
    json.dumps(sample.to_dict())
