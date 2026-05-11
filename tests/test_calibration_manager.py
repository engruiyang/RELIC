from ui_cli.run_calibration_debug import run_calibration
from storage.storage_manager import StorageManager
from user.user_manager import UserManager


def test_demo_first_and_quick_check(tmp_path):
    db = str(tmp_path / "cal.db")
    first = run_calibration("demo", db)
    assert first["valid"] is True
    assert first["calibration_type"] == "first_profile"
    assert first["system_state"] == "READY"

    second = run_calibration("demo", db)
    assert second["valid"] is True
    assert second["calibration_type"] == "quick_check"
    assert second["profile.last_calibration_id"] == second["calibration_id"]


def test_local_user_and_guest_and_failure(tmp_path):
    db = str(tmp_path / "cal2.db")
    s = StorageManager(sqlite_path=db)
    s.initialize()
    um = UserManager(s.sqlite)
    um.create_local_user_if_absent("TEST", "Test")
    s.shutdown()

    user_out = run_calibration("user", db, user_id="TEST")
    assert user_out["current_user_id"] == "TEST"

    guest_out = run_calibration("guest", db)
    assert guest_out["persisted"] is False

    fail_out = run_calibration("demo", db, fail=True)
    assert fail_out["valid"] is False
    assert fail_out["failure_reason"]
    assert fail_out["system_state"] == "CALIBRATION_FAILED"
