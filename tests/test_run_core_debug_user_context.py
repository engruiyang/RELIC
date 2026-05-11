from storage.storage_manager import StorageManager
from user.user_manager import UserManager
from user.profile_manager import ProfileManager
from calibration.calibration_manager import CalibrationManager
from ui_cli.run_core_debug import run_debug_loop


class _FakeGateway:
    def __init__(self, mode="mock", host="", port=0):
        self.mode = mode

    def start(self):
        return None

    def stop(self):
        return None

    def health(self):
        return {"connected": True, "alive": True}

    def poll_raw_events(self, now_ms):
        return [
            {"type": "device_status", "connected": True},
            {"type": "stream_status", "alive": True, "active": True},
            {"type": "attention", "value": 60},
            {"type": "gyroscope", "x": 1.0, "y": 2.0, "z": 3.0},
        ]


def _mk_user_and_store(db: str):
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um, pm = UserManager(s.sqlite), ProfileManager(s.sqlite)
    u, _ = um.create_local_user_if_absent("TEST", "Test")
    return s, um, pm, u


def test_run_core_debug_without_user_shows_no_user(monkeypatch, capsys):
    import ui_cli.run_core_debug as mod

    monkeypatch.setattr(mod, "PlatformGateway", _FakeGateway)
    run_debug_loop(mode="mock", host="127.0.0.1", port=8000, ticks=1, interval=0.001, user_mode=None, user_id=None)
    out = capsys.readouterr().out
    assert "quality_reasons=['no_profile', 'no_user']" in out or "quality_reasons=['no_user', 'no_profile']" in out


def test_run_core_debug_demo_mock_calibration_formal_false(tmp_path, monkeypatch, capsys):
    db = str(tmp_path / "a.db")
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um, pm = UserManager(s.sqlite), ProfileManager(s.sqlite)
    um.ensure_demo_user()
    s.shutdown()
    from ui_cli.run_calibration_debug import run_calibration_action
    run_calibration_action("start", "demo", db, source="mock", fast=True, progress=False, print_output=False)

    import ui_cli.run_core_debug as mod
    monkeypatch.setattr(mod, "PlatformGateway", _FakeGateway)
    run_debug_loop(mode="mock", host="127.0.0.1", port=8000, ticks=1, interval=0.001, user_mode="demo", db_path=db)
    out = capsys.readouterr().out
    assert "calibration_usable=True" in out
    assert "formal_training_allowed=False" in out
    assert "mock_calibration_debug_only" in out


def test_run_core_debug_user_ipc_calibration_formal_true(tmp_path, monkeypatch, capsys):
    db = str(tmp_path / "b.db")
    s, _, pm, u = _mk_user_and_store(db)
    cm = CalibrationManager(store=s, profile_manager=pm)
    gyro = [{"gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_fresh": True, "error_flags": []} for _ in range(20)]
    att = [{"attention": 60 + (i % 3), "attention_fresh": True, "error_flags": []} for i in range(20)]
    cp = cm.run_quick_calibration(user_id=u["user_id"], user_type=u["user_type"], device_id="ipc_device", gyro_snapshots=gyro, attention_snapshots=att, has_history=False, historical_baseline=None)
    s.save_calibration_profile(cp.to_dict())
    pm.update_last_calibration_id(u["user_id"], cp.calibration_id)
    s.shutdown()

    import ui_cli.run_core_debug as mod
    monkeypatch.setattr(mod, "PlatformGateway", _FakeGateway)
    run_debug_loop(mode="mock", host="127.0.0.1", port=8000, ticks=1, interval=0.001, user_mode="user", user_id="TEST", db_path=db)
    out = capsys.readouterr().out
    assert "calibration_usable=True" in out
    assert "formal_training_allowed=True" in out
    assert "bound_calibration_source=ipc" in out


def test_run_core_debug_user_no_calibration(tmp_path, monkeypatch, capsys):
    db = str(tmp_path / "c.db")
    s, _, _, _ = _mk_user_and_store(db)
    s.shutdown()
    import ui_cli.run_core_debug as mod
    monkeypatch.setattr(mod, "PlatformGateway", _FakeGateway)
    run_debug_loop(mode="mock", host="127.0.0.1", port=8000, ticks=1, interval=0.001, user_mode="user", user_id="TEST", db_path=db)
    out = capsys.readouterr().out
    assert "no_calibration" in out
