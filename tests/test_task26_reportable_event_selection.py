from pathlib import Path


def test_task26_pointer_click_public_event_ignores_non_reportable_semantic_events() -> None:
    text = Path("gui/gui_live_control_source.py").read_text(encoding="utf-8")
    assert "def _set_public_last_game_event" in text
    assert "public_event: dict[str, Any] | None = None" in text
    assert "if not evt.reportable:" in text
    assert "continue" in text
    assert "public_event = evt_dict" in text
    assert "dict(public_event or self.last_game_event)" in text
    assert "do not let them overwrite the user-action event" in text


def test_task26_tick_drain_only_platforms_reportable_events() -> None:
    text = Path("gui/gui_live_control_source.py").read_text(encoding="utf-8")
    drain_start = text.index("    def _drain_game_events")
    drain_end = text.index("    def _reset_training_buffers")
    drain = text[drain_start:drain_end]
    assert "self._record_training_event(evt_dict)" in drain
    assert "self.game_event_count += 1" in drain
    assert "if not evt.reportable:" in drain
    assert "self._set_public_last_game_event(evt_dict)" in drain
    assert drain.index("if not evt.reportable:") < drain.index("self._set_public_last_game_event(evt_dict)")
    assert drain.index("if not evt.reportable:") < drain.index("self._platform_adapter.process_game_event")
