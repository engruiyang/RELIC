import argparse
import time

from data.data_center import DataCenter
from relic_platform.platform_gateway import PlatformGateway
from core.quality_gate import QualityGate
from core.focus_estimator import FocusEstimator
from core.control_state_estimator import ControlStateEstimator
from storage.storage_manager import StorageManager
from user.user_manager import UserManager
from user.profile_manager import ProfileManager


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--mock", action="store_true")
    p.add_argument("--bridge", choices=["live", "mock"], default="mock")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--ticks", type=int, default=20)
    p.add_argument("--interval", type=float, default=0.5)
    p.add_argument("--mode", choices=["demo", "user", "guest"])
    p.add_argument("--user-id")
    p.add_argument("--db-path", default="data/relic_local.db")
    return p


def _resolve_user_context(mode: str | None, user_id: str | None, db_path: str):
    if mode is None:
        return None, None, None
    storage = StorageManager(sqlite_path=db_path)
    storage.initialize()
    um, pm = UserManager(storage.sqlite), ProfileManager(storage.sqlite)
    if mode == "guest":
        return um.enter_guest_mode(), None, storage
    if mode == "demo":
        u = um.ensure_demo_user()
        return u, pm.get_profile(u["user_id"]), storage
    if not user_id:
        raise ValueError("error: --mode user requires --user-id")
    u = um.load_user(user_id)
    if u is None:
        raise ValueError(f"user not found: {user_id}")
    return u, pm.get_profile(u["user_id"]), storage


def run_debug_loop(mode: str, host: str, port: int, ticks: int, interval: float, user_mode: str | None = None, user_id: str | None = None, db_path: str = "data/relic_local.db") -> None:
    gateway = PlatformGateway(mode=mode, host=host, port=port)
    data_center = DataCenter()
    quality_gate = QualityGate()
    focus_estimator = FocusEstimator()
    control_estimator = ControlStateEstimator()
    current_user, profile, storage = _resolve_user_context(user_mode, user_id, db_path)
    gateway.start()

    try:
        now_ms = 0
        tick_ms = int(interval * 1000)
        for i in range(1, ticks + 1):
            if mode == "live":
                h = gateway.health()
                if not h.get("connected") or not h.get("alive"):
                    print("Live bridge disconnected, exiting.")
                    break
            now_ms += tick_ms
            events = gateway.poll_raw_events(now_ms=now_ms)
            data_center.ingest_events(events, now_ms=now_ms)
            s = data_center.get_runtime_snapshot()
            bound = None
            bound_source = None
            binding_consistent = False
            if storage is not None and profile and profile.get("last_calibration_id"):
                bound = storage.get_calibration_profile(profile["last_calibration_id"])
                if bound is not None:
                    bound_source = "mock" if bound.get("device_id") == "mock_device" else "ipc"
                    binding_consistent = bool(bound.get("valid")) and bound.get("calibration_id") == profile.get("last_calibration_id")
            gate = quality_gate.evaluate(s, current_user=current_user, user_profile=profile, bound_calibration_profile=bound, warning_flags=s.get("warning_flags"), error_flags=s.get("error_flags"))
            data_center.apply_quality_gate(gate)
            s = data_center.get_runtime_snapshot()
            fi = focus_estimator.estimate(s, profile, bound)
            cs = control_estimator.evaluate(s, fi, tick_ms=tick_ms)
            s.update(fi)
            s.update(cs)
            print(
                f"tick={i} current_user_id={None if current_user is None else current_user['user_id']} "
                f"user_type={None if current_user is None else current_user['user_type']} "
                f"profile.last_calibration_id={None if profile is None else profile.get('last_calibration_id')} "
                f"bound_calibration_source={bound_source} binding_consistent={binding_consistent} "
                f"connected={s['device_connected']} stream_alive={s['stream_alive']} "
                f"sensor_stream_active={s['sensor_stream_active']} attention={s['attention']} "
                f"attention_age_ms={s['attention_age_ms']} attention_fresh={s['attention_fresh']} "
                f"attention_seen_once={s['attention_seen_once']} gyro={s['gyro']} gyro_age_ms={s['gyro_age_ms']} "
                f"gyro_fresh={s['gyro_fresh']} gyro_seen_once={s['gyro_seen_once']} "
                f"display_data_available={s['display_data_available']} training_data_valid={s['training_data_valid']} "
                f"control_data_valid={s['control_data_valid']} quality={s['quality']} "
                f"quality_reasons={s['quality_reasons']} warning_flags={s['warning_flags']} error_flags={s['error_flags']} "
                f"sqi={s['sqi']} quality_state={s['quality_state']} calibration_usable={s['calibration_usable']} "
                f"formal_training_allowed={s['formal_training_allowed']} signal_reliable={s['signal_reliable']} "
                f"estimation_allowed={s['estimation_allowed']} "
                f"s_eeg={s['s_eeg']} s_imu={s['s_imu']} s_b={s['s_b']} fi_raw={s['fi_raw']} fi_smoothed={s['fi_smoothed']} "
                f"fi_valid={s['fi_valid']} fi_confidence={s['fi_confidence']} control_state={s['control_state']} "
                f"control_state_reason={s['control_state_reason']}"
            )
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up...")
    finally:
        gateway.stop()
        if storage is not None:
            storage.shutdown()


def main() -> None:
    a = build_parser().parse_args()
    mode = "mock" if a.mock else a.bridge
    try:
        run_debug_loop(mode=mode, host=a.host, port=a.port, ticks=a.ticks, interval=a.interval, user_mode=a.mode, user_id=a.user_id, db_path=a.db_path)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up...")
    except ValueError as e:
        print(str(e))
    except Exception as e:
        print(f"[RELIC CORE] debug run failed: {e}. 建议先用 --bridge mock 验证。")


if __name__ == "__main__":
    main()
