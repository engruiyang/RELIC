from storage.storage_manager import StorageManager
from user.user_manager import UserManager
from ui_cli.run_calibration_debug import run_calibration_action


def _mk_user(db: str):
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um = UserManager(s.sqlite)
    um.create_local_user_if_absent("TEST", "Test")
    s.shutdown()


def test_mock_and_show_and_valid(tmp_path):
    db = str(tmp_path / "a.db")
    _mk_user(db)
    out = run_calibration_action("start", "user", db, user_id="TEST", source="mock", fast=True, progress=False, print_output=False)
    assert out["calibration_source"] == "mock"
    assert out["device_id"] == "mock_device"
    assert isinstance(out["valid"], bool)
    sh = run_calibration_action("show", None, db, calibration_id=out["calibration_id"], print_output=False)
    assert sh["calibration_user_id"] == "TEST"


def test_ipc_unavailable_no_fallback(tmp_path):
    db = str(tmp_path / "b.db")
    _mk_user(db)
    out = run_calibration_action("start", "user", db, user_id="TEST", source="ipc", fast=True, progress=False, print_output=False)
    assert out["valid"] is False
    assert out["failure_reason"] == "ipc_stream_unavailable"
    assert out["persisted"] is False
    assert out["calibration_source"] == "ipc"


def test_ipc_window_and_missing_cases(tmp_path):
    db = str(tmp_path / "c.db")
    _mk_user(db)
    # simulate short/missing via fast ipc path
    out = run_calibration_action("start", "user", db, user_id="TEST", source="ipc", fast=True, progress=False, print_output=False)
    assert out["failure_reason"] in {"ipc_stream_unavailable", "attention_window_too_short", "attention_missing", "gyro_missing"}


def test_verbose_events_and_error_message(tmp_path, capsys):
    import json, sys
    from ui_cli import run_calibration_debug as mod

    db = str(tmp_path / "d.db")
    _mk_user(db)
    out = run_calibration_action("start", "user", db, user_id="TEST", source="mock", fast=True, progress=False, verbose_events=True, print_output=False)
    evt = next(e for e in out["events"] if e["event_type"] == "calibration_phase_started")
    assert evt["user_instruction"] and evt["avoid_instruction"]

    old = sys.argv
    try:
        sys.argv = ["x", "--action", "start", "--mode", "user", "--user-id", "TEST", "--db-path", db, "--json-events", "--source", "mock", "--fast"]
        mod.main()
        parsed = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
        assert isinstance(parsed, list)

        sys.argv = ["x", "--action", "start", "--mode", "user", "--db-path", db]
        mod.main()
        txt = capsys.readouterr().out.lower()
        assert "traceback" not in txt
        assert "requires --user-id" in txt
    finally:
        sys.argv = old


def test_mode_userid_validation_and_ipc_device_id(tmp_path):
    db = str(tmp_path / "e.db")
    _mk_user(db)
    try:
        run_calibration_action("start", "demo", db, user_id="TEST", print_output=False)
        assert False
    except ValueError as e:
        assert "demo" in str(e)

    out = run_calibration_action("start", "user", db, user_id="TEST", source="ipc", fast=True, progress=False, print_output=False)
    assert out["calibration_source"] == "ipc"
    assert out.get("persisted") is False


def test_list_latest_show_include_source(tmp_path):
    db = str(tmp_path / "f.db")
    _mk_user(db)
    m = run_calibration_action("start", "user", db, user_id="TEST", source="mock", fast=True, progress=False, print_output=False)
    lst = run_calibration_action("list", "user", db, user_id="TEST", print_output=False)
    assert "calibration_source" in lst["calibrations"][0]
    lat = run_calibration_action("latest", "user", db, user_id="TEST", print_output=False)
    assert lat["calibration_source"] in {"mock", "ipc"}
    sh = run_calibration_action("show", None, db, calibration_id=m["calibration_id"], print_output=False)
    assert sh["calibration_source"] in {"mock", "ipc"}
