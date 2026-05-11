import argparse
import time

from data.data_center import DataCenter
from relic_platform.platform_gateway import PlatformGateway
from core.quality_gate import QualityGate


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--mock", action="store_true")
    p.add_argument("--bridge", choices=["live", "mock"], default="mock")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--ticks", type=int, default=20)
    p.add_argument("--interval", type=float, default=0.5)
    return p


def run_debug_loop(mode: str, host: str, port: int, ticks: int, interval: float) -> None:
    gateway = PlatformGateway(mode=mode, host=host, port=port)
    data_center = DataCenter()
    quality_gate = QualityGate()
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
            gate = quality_gate.evaluate(s, current_user=None, user_profile=None, bound_calibration_profile=None, warning_flags=s.get("warning_flags"), error_flags=s.get("error_flags"))
            data_center.apply_quality_gate(gate)
            s = data_center.get_runtime_snapshot()
            print(
                f"tick={i} connected={s['device_connected']} stream_alive={s['stream_alive']} "
                f"sensor_stream_active={s['sensor_stream_active']} attention={s['attention']} "
                f"attention_age_ms={s['attention_age_ms']} attention_fresh={s['attention_fresh']} "
                f"attention_seen_once={s['attention_seen_once']} gyro={s['gyro']} gyro_age_ms={s['gyro_age_ms']} "
                f"gyro_fresh={s['gyro_fresh']} gyro_seen_once={s['gyro_seen_once']} "
                f"display_data_available={s['display_data_available']} training_data_valid={s['training_data_valid']} "
                f"control_data_valid={s['control_data_valid']} quality={s['quality']} "
                f"quality_reasons={s['quality_reasons']} warning_flags={s['warning_flags']} error_flags={s['error_flags']} "
                f"sqi={s['sqi']} quality_state={s['quality_state']} calibration_usable={s['calibration_usable']} "
                f"formal_training_allowed={s['formal_training_allowed']} signal_reliable={s['signal_reliable']} "
                f"estimation_allowed={s['estimation_allowed']}"
            )
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up...")
    finally:
        gateway.stop()


def main() -> None:
    a = build_parser().parse_args()
    mode = "mock" if a.mock else a.bridge
    try:
        run_debug_loop(mode=mode, host=a.host, port=a.port, ticks=a.ticks, interval=a.interval)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up...")
    except Exception as e:
        print(f"[RELIC CORE] debug run failed: {e}. 建议先用 --bridge mock 验证。")


if __name__ == "__main__":
    main()
