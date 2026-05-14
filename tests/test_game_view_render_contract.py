from __future__ import annotations

import json

from game.fake_click_game_client import FakeClickGameClient
from gui.gui_facade import GuiFacade
from gui.gui_mouse_input_router import GuiMouseInputRouter


def test_fake_click_game_view_entities_contract() -> None:
    client = FakeClickGameClient()
    client.start({"session_id": "s1", "game_id": "fake_game"})
    view = client.build_game_view().to_dict()
    kinds = {e["kind"] for e in view["entities"]}
    assert {"target", "focus_zone", "progress_ring"}.issubset(kinds)
    for entity in view["entities"]:
        assert 0.0 <= entity["x"] <= 1.0
        assert 0.0 <= entity["y"] <= 1.0
        assert 0.0 <= entity["radius"] <= 1.0
        assert "/" not in entity.get("asset_key", "")
        assert "\\\\" not in entity.get("asset_key", "")


def test_pointer_click_routes_and_exposes_game_view_json() -> None:
    facade = GuiFacade(mode="core-control", duration_sec=1)
    facade.handle_gui_command("start_mock_session", {})
    facade.handle_gui_event("pointer_click", {"game_id": "fake_game", "x_norm": 0.5, "y_norm": 0.5, "button": "left", "source": "test"})
    game_view = facade.get_game_view()
    assert game_view.get("entities")
    json.loads(json.dumps(game_view))
    assert facade.last_game_event.get("event_type") in {"target_click", "background_click"}


def test_router_accepts_pointer_click() -> None:
    router = GuiMouseInputRouter(game_id="fake_game")
    out = router.route_gui_event(event_type="pointer_click", payload={"game_id": "fake_game", "x_norm": 0.1, "y_norm": 0.1, "button": "left"}, session_id="sid")
    assert out["status"] == "accepted"
    assert out["last_game_event"]["event_type"] in {"target_click", "background_click"}
