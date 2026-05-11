from storage.storage_manager import StorageManager
from user.user_manager import UserManager
from ui_cli.run_calibration_debug import run_calibration_action


def test_status_start_list_latest_show_bind_cancel_guest(tmp_path):
    db = str(tmp_path / "m.db")
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um = UserManager(s.sqlite)
    um.create_local_user_if_absent("TEST", "Test")
    s.shutdown()

    st0 = run_calibration_action("status", "user", db, user_id="TEST")
    assert st0["profile.last_calibration_id"] is None
    assert st0["latest_calibration_id"] is None

    first = run_calibration_action("start", "user", db, user_id="TEST", calibration_type="auto")
    assert first["calibration_type"] == "first_profile"
    second = run_calibration_action("start", "user", db, user_id="TEST", calibration_type="auto")
    assert second["calibration_type"] == "quick_check"

    lst = run_calibration_action("list", "user", db, user_id="TEST")
    assert lst["calibration_count"] >= 2
    assert any(i["is_bound_to_profile"] for i in lst["calibrations"])

    latest = run_calibration_action("latest", "user", db, user_id="TEST")
    cid = latest["calibration_id"]
    sh = run_calibration_action("show", "demo", db, calibration_id=cid)
    assert sh["calibration_id"] == cid

    # invalid bind should fail
    bad = run_calibration_action("start", "demo", db, calibration_type="auto", fail=True)
    try:
        run_calibration_action("bind", "demo", db, calibration_id=bad["calibration_id"])
        assert False
    except ValueError as e:
        assert str(e) == "invalid_calibration"

    try:
        run_calibration_action("bind", "user", db, user_id="TEST", calibration_id=first["calibration_id"])
    except Exception:
        pass

    try:
        run_calibration_action("bind", "user", db, user_id="TEST", calibration_id=bad["calibration_id"])
        assert False
    except ValueError:
        pass

    cancel = run_calibration_action("cancel", "user", db, user_id="TEST")
    assert cancel["failure_reason"] == "cancelled_by_user"
    assert cancel["system_state"] == "CALIBRATION_FAILED"

    guest = run_calibration_action("start", "guest", db)
    assert guest["persisted"] is False


def test_show_owner_viewer_semantics_and_bool(tmp_path):
    db = str(tmp_path / "show.db")
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um = UserManager(s.sqlite)
    um.create_local_user_if_absent("TEST", "Test")
    s.shutdown()

    created = run_calibration_action("start", "user", db, user_id="TEST", calibration_type="auto")
    shown = run_calibration_action("show", None, db, calibration_id=created["calibration_id"])
    assert "current_user_id" not in shown
    assert shown["calibration_user_id"] == "TEST"
    assert isinstance(shown["valid"], bool)

    shown2 = run_calibration_action("show", "demo", db, calibration_id=created["calibration_id"])
    assert shown2["calibration_user_id"] == "TEST"
    assert shown2["viewer_user_id"] == "demo"
    assert shown2["viewer_user_type"] == "demo"

    latest = run_calibration_action("latest", "user", db, user_id="TEST")
    assert isinstance(latest["valid"], bool)


def test_start_events_fast_and_progress_failure_and_cancel(tmp_path):
    db = str(tmp_path / "evt.db")
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um = UserManager(s.sqlite)
    um.create_local_user_if_absent("TEST", "Test")
    s.shutdown()

    out = run_calibration_action("start", "user", db, user_id="TEST", calibration_type="auto", fast=True, progress=False, verbose_events=True)
    event_types = [e["event_type"] for e in out["events"]]
    assert "calibration_started" in event_types
    assert "calibration_progress" in event_types
    assert "calibration_completed" in event_types

    fail = run_calibration_action("start", "demo", db, calibration_type="auto", fail=True, fast=True, progress=False, verbose_events=True)
    fail_types = [e["event_type"] for e in fail["events"]]
    assert "calibration_failed" in fail_types

    cancel = run_calibration_action("cancel", "user", db, user_id="TEST", fast=True, progress=False, verbose_events=True)
    cancel_types = [e["event_type"] for e in cancel["events"]]
    assert "calibration_cancelled" in cancel_types


def test_event_includes_user_instructions_and_default_no_events(tmp_path):
    db = str(tmp_path / "tips.db")
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um = UserManager(s.sqlite)
    um.create_local_user_if_absent("TEST", "Test")
    s.shutdown()

    out_default = run_calibration_action("start", "user", db, user_id="TEST", fast=True, progress=False)
    assert "events" not in out_default

    out_verbose = run_calibration_action("start", "user", db, user_id="TEST", fast=True, progress=False, verbose_events=True)
    evt = next(e for e in out_verbose["events"] if e["event_type"] == "calibration_phase_started")
    assert evt["user_instruction"]
    assert evt["avoid_instruction"]
    assert evt["title"]

    out_fail = run_calibration_action("start", "demo", db, fail=True, fast=True, progress=False)
    assert out_fail["user_recovery_hint"]


def test_json_events_parseable_and_user_error_message(tmp_path, capsys):
    import json
    import sys
    from ui_cli import run_calibration_debug as mod

    db = str(tmp_path / "json.db")
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um = UserManager(s.sqlite)
    um.create_local_user_if_absent("TEST", "Test")
    s.shutdown()

    old = sys.argv
    try:
        sys.argv = ["run_calibration_debug", "--action", "start", "--mode", "user", "--user-id", "TEST", "--db-path", db, "--json-events", "--fast"]
        mod.main()
        out = capsys.readouterr().out.strip().splitlines()[-1]
        parsed = json.loads(out)
        assert isinstance(parsed, list)

        sys.argv = ["run_calibration_debug", "--action", "start", "--mode", "user", "--db-path", db]
        mod.main()
        err = capsys.readouterr().out
        assert "traceback" not in err.lower()
        assert "--mode user requires --user-id" in err
    finally:
        sys.argv = old
