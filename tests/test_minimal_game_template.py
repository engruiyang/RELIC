from pathlib import Path

from game.game_contracts import BehaviorSample, GameInputEvent, GameViewState
from game.templates.minimal_game.minimal_game_client import MinimalGameClient


def _evt(x: float, y: float, button: int = 0) -> GameInputEvent:
    return GameInputEvent(
        event_id="evt-1",
        session_id="sess-1",
        game_id="minimal_template",
        input_type="pointer_click",
        created_at_ms=123456,
        source="pytest",
        x_norm=x,
        y_norm=y,
        button=button,
        raw_event_type="mouse_press",
    )


def test_minimal_game_client_basics() -> None:
    client = MinimalGameClient()
    client.start({"session_id": "sess-1"})
    assert client.get_score() == 0

    view = client.build_game_view()
    assert isinstance(view, GameViewState)
    assert any(e.kind == "target" for e in view.entities)
    target = next(e for e in view.entities if e.kind == "target")
    assert target.asset_key and target.style_key
    assert "assets/" not in target.asset_key
    assert ".png" not in target.asset_key


def test_target_and_background_click_events() -> None:
    client = MinimalGameClient()
    client.start({})
    client.handle_input(_evt(0.5, 0.5))
    events = client.collect_game_events()
    assert any(e.event_type == "target_click" for e in events)

    client.handle_input(_evt(0.05, 0.05))
    events = client.collect_game_events()
    assert any(e.event_type == "background_click" for e in events)


def test_collect_behavior_sample() -> None:
    client = MinimalGameClient()
    client.start({})
    client.handle_input(_evt(0.5, 0.5))
    sample = client.collect_behavior_sample()
    assert isinstance(sample, BehaviorSample)


def test_template_source_has_no_forbidden_runtime_dependencies() -> None:
    source = Path("game/templates/minimal_game/minimal_game_client.py").read_text(encoding="utf-8")
    lowered = source.lower()
    assert "platformreporter" not in lowered
    assert "ipc_mouse_data" not in lowered
    assert "pyside6" not in lowered
    assert "sqlite" not in lowered
    assert "assets/" not in lowered
    assert ".png" not in lowered
