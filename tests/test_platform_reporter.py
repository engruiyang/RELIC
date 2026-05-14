from relic_platform.platform_reporter import PlatformReporter


def test_platform_reporter_builders_and_mapping():
    r = PlatformReporter()
    mouse = r.build_mouse_list({"supported_event_types": ["a", "b"]})
    assert mouse["type"] == "ipc_mouse_list"
    start = r.build_test_start({"session_id": "s1", "user_id": "u1", "game_id": "g1"})
    assert start["type"] == "ipc_test_start"
    stop = r.build_test_stop({"session_id": "s1", "score": 1.0, "status": "ended"})
    assert stop["type"] == "ipc_test_stop"
    md = r.map_game_event_to_mouse_data({"event_type": "target_click", "session_id": "s1", "created_at_ms": 123, "payload": {"target_index": 7}})
    assert md and md["type"] == "ipc_mouse_data" and md["index"] == 7


def test_platform_reporter_handle_algorithm_stop_test():
    r = PlatformReporter()
    res = r.handle_algorithm_stop_test({"session_id": "s1", "uploaded": False, "error_reason": "bad"})
    assert res.status == "failed"
    assert r.get_report_result("s1") is not None
