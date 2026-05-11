from __future__ import annotations

import argparse
import json
import time

from calibration.calibration_manager import CalibrationManager
from core.state_machine import StateMachine, SystemState
from data.data_center import DataCenter
from platform.platform_gateway import PlatformGateway
from storage.storage_manager import StorageManager
from user.profile_manager import ProfileManager
from user.user_manager import UserManager


def _build_samples(fail: bool = False) -> tuple[list[dict], list[dict]]:
    gyro, att = [], []
    for i in range(60):
        gyro.append({"gyro_x": 0.01 * (i % 3), "gyro_y": -0.01 * (i % 2), "gyro_z": 0.02, "gyro_fresh": True, "error_flags": []})
    for i in range(120):
        att.append({"attention": (0 if fail else 55 + (i % 5)), "attention_fresh": True, "error_flags": []})
    return gyro, att


def _collect_ipc_samples(host: str, port: int, fast: bool) -> tuple[list[dict], list[dict], dict]:
    if fast:
        return [], [], {"ipc_connected": False, "live_data_detected": False, "failure_reason": "ipc_stream_unavailable"}
    phase_ms = {"preparation": 2000, "gyro": 3000, "attention": 8000, "result": 1000}
    gateway = PlatformGateway(mode="live", host=host, port=port)
    dc = DataCenter()
    now = 0
    gyro_samples, att_samples = [], []
    try:
        gateway.start()
        h = gateway.health()
        if not h.get("connected"):
            return [], [], {"ipc_connected": False, "live_data_detected": False, "failure_reason": "ipc_stream_unavailable"}
        total = sum(phase_ms.values())
        interval = 100
        while now < total:
            now += interval
            events = gateway.poll_raw_events(now_ms=now)
            dc.ingest_events(events, now_ms=now)
            s = dc.get_runtime_snapshot()
            if phase_ms["preparation"] < now <= phase_ms["preparation"] + phase_ms["gyro"]:
                gyro_samples.append(s)
            if now > phase_ms["preparation"] + phase_ms["gyro"] and now <= phase_ms["preparation"] + phase_ms["gyro"] + phase_ms["attention"]:
                att_samples.append(s)
            time.sleep(interval / 1000)
        return gyro_samples, att_samples, {"ipc_connected": True, "live_data_detected": bool(gyro_samples or att_samples), "failure_reason": None}
    finally:
        gateway.stop()


def _load_user(mode: str | None, user_id: str | None, um: UserManager, pm: ProfileManager):
    resolved_mode = mode or "demo"
    if resolved_mode == "guest":
        return um.enter_guest_mode(), None
    if resolved_mode == "user":
        if not user_id:
            raise ValueError("error: --mode user requires --user-id\nexample: python -m ui_cli.run_calibration_debug --action start --mode user --user-id TEST --calibration-type auto")
        user = um.load_user(user_id)
        if user is None:
            raise ValueError(f"user not found: {user_id}")
        return user, pm.get_profile(user["user_id"])
    user = um.ensure_demo_user()
    return user, pm.get_profile(user["user_id"])


def run_calibration_action(action: str, mode: str | None, db_path: str, user_id: str | None = None, calibration_type: str = "auto", calibration_id: str | None = None, fail: bool = False, fast: bool = True, progress: bool = True, verbose_events: bool = False, json_events: bool = False, print_output: bool = True, source: str = "mock", host: str = "127.0.0.1", port: int = 8000) -> dict:
    storage = StorageManager(sqlite_path=db_path)
    storage.initialize()
    sm = StateMachine()
    sm.transition(SystemState.NO_USER)
    um, pm = UserManager(storage.sqlite), ProfileManager(storage.sqlite)
    cm = CalibrationManager(store=storage, profile_manager=pm)
    user = None
    profile = None
    if action in {"status", "start", "cancel", "list", "latest", "bind"}:
        user, profile = _load_user(mode, user_id, um, pm)
        sm.transition(SystemState.USER_READY)
    out = {"db_path": db_path}
    if user is not None:
        out |= {"current_user_id": user["user_id"], "user_type": user["user_type"]}

    if action == "start":
        sm.transition(SystemState.CALIBRATING)
        print(f"[calibration] source={source}" + (f" host={host} port={port}" if source == "ipc" else ""))
        events = []

        def on_event(e):
            events.append(e)
            if progress and e.get("event_type") == "calibration_phase_started":
                print(f"[phase {e['phase_index']}/{e['phase_count']}] {e['title']}")
                print(f"  {e['user_instruction']}")
                print(f"  {e['avoid_instruction']}")

        if source == "ipc":
            gyro, att, ipc_meta = _collect_ipc_samples(host, port, fast)
            out |= ipc_meta
            if ipc_meta.get("failure_reason"):
                out.update({"valid": False, "persisted": False, "calibration_source": "ipc", "failure_reason": ipc_meta["failure_reason"], "user_recovery_hint": "未检测到平台 IPC 数据。请确认科创平台已启动、端口配置正确，并已进入范式页面。", "system_state": SystemState.CALIBRATION_FAILED.value})
                if verbose_events or json_events:
                    out["events"] = events
                storage.shutdown()
                if print_output:
                    for k, v in out.items(): print(f"{k}={v}")
                return out
            attention_window_ms = 8000
            gyro_window_ms = 3000
        else:
            gyro, att = _build_samples(fail=fail)
            attention_window_ms = 2000 if fast else 8000
            gyro_window_ms = 1000 if fast else 3000
            out["ipc_connected"] = False
            out["live_data_detected"] = False

        cp = cm.start_calibration(user, calibration_type, gyro, att, fast=fast, emit_event=on_event)
        out |= cp.to_dict()
        out["valid"] = bool(out["valid"])
        out["calibration_source"] = source
        out["fast_mode"] = bool(fast)
        out["attention_window_ms"] = attention_window_ms
        out["gyro_window_ms"] = gyro_window_ms
        out["attention_sample_count"] = len(att)
        out["attention_unique_update_count"] = len({x.get("attention") for x in att if x.get("attention") is not None})
        out["gyro_sample_count"] = len(gyro)
        out["baseline_confidence"] = "mock" if source == "mock" else ("high" if out["valid"] else "low")
        out["persisted"] = (user["user_type"] != "guest" and out["valid"])
        out["profile.last_calibration_id"] = None if user["user_type"] == "guest" else pm.get_profile(user["user_id"])["last_calibration_id"]
        out["user_recovery_hint"] = cm.get_recovery_hint(cp.failure_reason)
        if source == "ipc":
            if out["attention_window_ms"] < 8000:
                out["valid"] = False; out["failure_reason"] = "attention_window_too_short"
            if out["gyro_window_ms"] < 3000:
                out["valid"] = False; out["failure_reason"] = "gyro_window_too_short"
            if out["attention_sample_count"] == 0:
                out["valid"] = False; out["failure_reason"] = "attention_missing"
            if out["gyro_sample_count"] == 0:
                out["valid"] = False; out["failure_reason"] = "gyro_missing"
            if out["attention_unique_update_count"] < 2 and out["valid"]:
                out["baseline_confidence"] = "low"; out["failure_reason"] = "attention_update_too_sparse"; out["valid"] = False
            out["persisted"] = out["persisted"] and out["valid"]
            out["user_recovery_hint"] = cm.get_recovery_hint(out.get("failure_reason"))
        sm.transition(SystemState.READY if out["valid"] else SystemState.CALIBRATION_FAILED)
        if verbose_events or json_events:
            out["events"] = events
    else:
        # keep previous actions minimal
        if action == "status": out |= cm.get_calibration_status(user["user_id"])
        elif action == "latest":
            latest = cm.get_latest_calibration(user["user_id"]) if user["user_type"] != "guest" else None
            out |= ({"latest": None} if latest is None else {**latest, "valid": bool(latest["valid"])})
        elif action == "list":
            items = [] if user["user_type"] == "guest" else cm.list_calibrations(user["user_id"])
            bound = None if profile is None else profile.get("last_calibration_id")
            out["calibrations"] = [{**i, "valid": bool(i["valid"]), "is_bound_to_profile": i["calibration_id"] == bound} for i in items]
            out["calibration_count"] = len(items)
        elif action == "show":
            cp = cm.get_calibration(calibration_id)
            if cp is None: raise ValueError("calibration_not_found")
            out |= {**cp, "valid": bool(cp["valid"]), "calibration_user_id": cp["user_id"]}
            out.pop("user_id", None)
        elif action == "bind":
            old, new = cm.bind_calibration_to_profile(user["user_id"], calibration_id)
            out["old_last_calibration_id"], out["new_last_calibration_id"] = old, new
        elif action == "cancel":
            cp = cm.cancel_calibration(user); out |= cp.to_dict(); out["valid"] = False

    out["system_state"] = sm.state.value
    if print_output:
        for k, v in out.items(): print(f"{k}={v}")
    storage.shutdown()
    return out


def run_calibration(mode: str, db_path: str, user_id: str | None = None, fail: bool = False) -> dict:
    return run_calibration_action("start", mode, db_path, user_id=user_id, fail=fail, fast=True, progress=False, source="mock", print_output=False)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--action", choices=["status", "start", "cancel", "list", "latest", "show", "bind"], default="start")
    p.add_argument("--mode", choices=["demo", "user", "guest"], default=None)
    p.add_argument("--user-id")
    p.add_argument("--db-path", default="data/relic_local.db")
    p.add_argument("--calibration-type", choices=["auto", "first_profile", "quick_check", "periodic", "triggered"], default="auto")
    p.add_argument("--calibration-id")
    p.add_argument("--fail", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--no-progress", action="store_true")
    p.add_argument("--verbose-events", action="store_true")
    p.add_argument("--json-events", action="store_true")
    p.add_argument("--source", choices=["mock", "ipc", "auto"], default="mock")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    a = p.parse_args()
    source = "mock" if a.source == "auto" else a.source
    try:
        r = run_calibration_action(a.action, a.mode, a.db_path, a.user_id, a.calibration_type, a.calibration_id, a.fail, fast=a.fast, progress=not a.no_progress, verbose_events=a.verbose_events, json_events=a.json_events, print_output=not a.json_events, source=source, host=a.host, port=a.port)
        if a.json_events:
            print(json.dumps(r.get("events", []), ensure_ascii=False))
    except ValueError as e:
        print(f"error: {e}")


if __name__ == "__main__":
    main()
