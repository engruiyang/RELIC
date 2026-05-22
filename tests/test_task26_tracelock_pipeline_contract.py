from pathlib import Path
import json


def test_task26_live_control_training_log_records_runtime_and_game_events() -> None:
    text = Path("gui/gui_live_control_source.py").read_text(encoding="utf-8")
    for token in [
        "_normalize_training_runtime_sample",
        "_derive_fi_from_runtime",
        "_derive_sqi_from_runtime",
        "_training_events",
        "runtime_sample",
        "behavior_sample_snapshot",
        "game_event",
        "fi_source_summary",
        "sqi_source_summary",
        "calibration_id",
        "calibration_profile",
        "attention_baseline",
        "attention_std",
    ]:
        assert token in text


def test_task26_trace_lock_emits_replayable_semantic_events() -> None:
    text = Path("game/examples/trace_lock/trace_lock_client.py").read_text(encoding="utf-8")
    for token in [
        "target_spawn",
        "target_click",
        "background_click",
        "target_omitted",
        "score_update",
        "game_completed",
        "reaction_time_ms",
        "score_delta",
        "trace_drop",
        "trace_seal",
    ]:
        assert token in text


def test_task26_replay_adapter_accepts_type_and_event_type_records(tmp_path) -> None:
    from storage.replay_adapter import ReplayAdapter

    log_path = tmp_path / "mixed.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps({"type": "runtime_sample", "payload": {"fi": 72}}),
                json.dumps({"event_type": "game_event", "payload": {"event_type": "target_click"}}),
                json.dumps({"type": "behavior_sample", "payload": {"accuracy": 1.0}}),
            ]
        ),
        encoding="utf-8",
    )
    summary = ReplayAdapter().summarize(str(log_path))
    assert summary["event_count"] == 3
    assert summary["event_type_counts"]["runtime_sample"] == 1
    assert summary["event_type_counts"]["game_event"] == 1
    assert summary["event_type_counts"]["behavior_sample"] == 1
