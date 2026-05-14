import json
from storage.replay_adapter import ReplayAdapter


def test_replay_adapter_load_filter_summarize(tmp_path):
    p = tmp_path / "a.jsonl"
    rows = [
        {"event_type": "runtime_snapshot", "payload": {"now_ms": 1000}},
        {"event_type": "game_event", "payload": {"now_ms": 1500}},
        {"event_type": "warning", "payload": {}},
    ]
    p.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    ra = ReplayAdapter()
    assert len(ra.load_events(str(p))) == 3
    assert len(list(ra.iter_events(str(p), {"game_event"}))) == 1
    sm = ra.summarize(str(p))
    assert sm["event_count"] == 3
    stats = ra.replay(str(p), speed=0)
    assert stats["event_count"] == 3
