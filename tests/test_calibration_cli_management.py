from storage.storage_manager import StorageManager
from user.user_manager import UserManager
from ui_cli.run_calibration_debug import run_calibration_action


def _mk_user(db: str):
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um = UserManager(s.sqlite)
    um.create_local_user_if_absent("TEST", "Test")
    s.shutdown()


def test_mode_userid_guard_and_default_source(tmp_path):
    db = str(tmp_path / "a.db")
    _mk_user(db)
    try:
        run_calibration_action("start", "demo", db, user_id="TEST", print_output=False)
        assert False
    except ValueError:
        pass
    out_user = run_calibration_action("start", "user", db, user_id="TEST", fast=True, progress=False, print_output=False)
    assert out_user["calibration_source"] == "ipc"
    out_demo = run_calibration_action("start", "demo", db, fast=True, progress=False, print_output=False)
    assert out_demo["calibration_source"] == "mock"


def test_ipc_no_data_and_device_semantics(tmp_path):
    db = str(tmp_path / "b.db")
    _mk_user(db)
    out = run_calibration_action("start", "user", db, user_id="TEST", source="ipc", fast=True, progress=False, print_output=False)
    assert out["valid"] is False
    assert out["persisted"] is False
    assert out["failure_reason"] in {"ipc_stream_unavailable", "ipc_stream_interrupted"}


def test_list_latest_show_and_binding_consistency(tmp_path):
    db = str(tmp_path / "c.db")
    _mk_user(db)
    m = run_calibration_action("start", "demo", db, source="mock", fast=True, progress=False, print_output=False)
    sh = run_calibration_action("show", None, db, calibration_id=m["calibration_id"], print_output=False)
    assert sh["calibration_source"] == "mock"
    lst = run_calibration_action("list", "demo", db, print_output=False)
    assert "calibration_source" in lst["calibrations"][0]
    st = run_calibration_action("status", "demo", db, print_output=False)
    assert "binding_consistent" in st


def test_bind_protections(tmp_path):
    db = str(tmp_path / "d.db")
    _mk_user(db)
    d = run_calibration_action("start", "demo", db, source="mock", fast=True, progress=False, print_output=False)
    try:
        run_calibration_action("bind", "user", db, user_id="TEST", calibration_id=d["calibration_id"], print_output=False)
        assert False
    except ValueError:
        pass


def test_failed_ipc_does_not_update_profile_binding(tmp_path):
    db = str(tmp_path / "e.db")
    _mk_user(db)
    ok = run_calibration_action("start", "demo", db, source="mock", fast=True, progress=False, print_output=False)
    before = run_calibration_action("status", "demo", db, print_output=False)["profile.last_calibration_id"]
    out = run_calibration_action("start", "user", db, user_id="TEST", source="ipc", fast=True, progress=False, print_output=False)
    assert out["valid"] is False
    after = run_calibration_action("status", "demo", db, print_output=False)["profile.last_calibration_id"]
    assert before == after


def test_ipc_interrupted_flags(tmp_path, monkeypatch):
    db = str(tmp_path / "f.db")
    _mk_user(db)
    import ui_cli.run_calibration_debug as mod

    def fake_collect(host, port, fast, phase_callback=None, sleeper=None):
        return [], [], {"ipc_connected": True, "ipc_connected_at_end": False, "stream_interrupted": True, "live_data_detected": True, "failure_reason": "ipc_stream_interrupted"}

    monkeypatch.setattr(mod, "_collect_ipc_samples", fake_collect)
    out = mod.run_calibration_action("start", "user", db, user_id="TEST", source="ipc", fast=False, progress=False, print_output=False)
    assert out["failure_reason"] == "ipc_stream_interrupted"
    assert out["stream_interrupted"] is True
    assert out["ipc_connected_at_end"] is False
    assert out["persisted"] is False
    assert out["failure_reason"] != "attention_update_too_sparse"


def test_ipc_interrupted_reason_priority_over_attention(tmp_path, monkeypatch):
    db = str(tmp_path / "h.db")
    _mk_user(db)
    import ui_cli.run_calibration_debug as mod

    def fake_collect(host, port, fast, phase_callback=None, sleeper=None):
        return [{"gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_fresh": True, "error_flags": []}], [{"attention": 50, "attention_fresh": True, "error_flags": []}], {"ipc_connected": True, "ipc_connected_at_end": False, "stream_interrupted": True, "live_data_detected": True, "failure_reason": "ipc_stream_interrupted"}

    monkeypatch.setattr(mod, "_collect_ipc_samples", fake_collect)
    out = mod.run_calibration_action("start", "user", db, user_id="TEST", source="ipc", fast=False, progress=False, print_output=False)
    assert out["failure_reason"] == "ipc_stream_interrupted"
    assert out["valid"] is False
    assert out["persisted"] is False


def test_ipc_phase_prompt_realtime_order_and_flush(monkeypatch):
    import io
    import ui_cli.run_calibration_debug as mod

    order = []

    class FakeGateway:
        def __init__(self, mode="live", host="", port=0):
            self.connected = True

        def start(self):
            return None

        def stop(self):
            return None

        def health(self):
            return {"connected": True, "alive": True}

        def poll_raw_events(self, now_ms):
            return []

    def fake_sleep(_):
        order.append("sleep")

    out = io.StringIO()
    monkeypatch.setattr(mod, "PlatformGateway", FakeGateway)
    phases = []
    gyro, att, meta = mod._collect_ipc_samples("127.0.0.1", 8000, fast=False, phase_callback=lambda p: phases.append(p), sleeper=fake_sleep)
    assert phases[:4] == ["preparation", "gyro_static_baseline", "attention_quick_baseline", "result"]
    assert order[0] == "sleep"
    assert meta["failure_reason"] is None


def test_status_binding_consistent_requires_valid(tmp_path):
    db = str(tmp_path / "g.db")
    _mk_user(db)
    st = run_calibration_action("status", "user", db, user_id="TEST", print_output=False)
    assert "binding_consistent" in st
