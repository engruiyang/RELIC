#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import socket
import struct
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def pack_frame(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return struct.pack(">I", len(body)) + body


@dataclass
class GyroSample:
    timestamp_utc: str
    monotonic_ms: int
    session_id: str
    source_msg: str
    algorithm_name: str | None
    focus_x: float | int | None
    focus_y: float | int | None
    focus_area_x: float | int | None
    focus_area_y: float | int | None
    focus_area_width: float | int | None
    focus_area_height: float | int | None
    gyro_x: float | int | None
    gyro_y: float | int | None
    gyro_z: float | int | None
    valid: bool
    raw: dict[str, Any]


class FrameParser:
    def __init__(self) -> None:
        self._buffer = bytearray()

    def feed(self, data: bytes) -> list[tuple[dict[str, Any], str]]:
        self._buffer.extend(data)
        out: list[tuple[dict[str, Any], str]] = []
        while True:
            if len(self._buffer) < 4:
                break
            payload_len = struct.unpack(">I", self._buffer[:4])[0]
            total_len = 4 + payload_len
            if len(self._buffer) < total_len:
                break
            payload_bytes = bytes(self._buffer[4:total_len])
            del self._buffer[:total_len]
            payload_text = payload_bytes.decode("utf-8")
            obj = json.loads(payload_text)
            if isinstance(obj, dict):
                out.append((obj, payload_text))
        return out


class RelicClient:
    def __init__(self, host: str, port: int, print_attention: bool, verbose: bool, dump_raw: bool, raw_limit: int, save_payload_text: bool) -> None:
        self.host, self.port = host, port
        self.print_attention = print_attention
        self.verbose = verbose
        self.dump_raw = dump_raw
        self.raw_limit = raw_limit
        self.save_payload_text = save_payload_text
        self.raw_dump_count = 0

        now_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = now_tag
        self.raw_log = Path(f"logs/raw/ipc_raw_{now_tag}.jsonl")
        self.decode_err_log = Path(f"logs/raw/ipc_decode_error_{now_tag}.jsonl")
        self.sensor_log = Path(f"logs/session/session_{now_tag}_sensor.jsonl")
        self.raw_log.parent.mkdir(parents=True, exist_ok=True)
        self.sensor_log.parent.mkdir(parents=True, exist_ok=True)

        self.sock: socket.socket | None = None
        self.parser = FrameParser()
        self.running = False
        self.window_id: int | None = None

        self.connected = False
        self.layout_type: int | None = None
        self.last_msg: str | None = None
        self.last_algorithm_name: str | None = None
        self.attention_value: int | None = None
        self.attention_valid = False
        self.attention_ts_ms: int | None = None
        self.focus_x = self.focus_y = None
        self.gyro_x = self.gyro_y = self.gyro_z = None
        self.gyro_valid = False
        self.gyro_ts_ms: int | None = None
        self.blink_state = None
        self.device_connected = None
        self.device_wear = None
        self.battery = None
        self.sample_rate = None

    def mono_ms(self) -> int:
        return int(time.monotonic() * 1000)

    def connect(self) -> None:
        self.sock = socket.create_connection((self.host, self.port))
        self.running = True
        self.connected = True
        print(f"已连接科创平台 {self.host}:{self.port}")

    def close(self) -> None:
        self.running = False
        self.connected = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.sock.close()
            self.sock = None

    def send_message(self, payload: dict[str, Any]) -> None:
        if not self.sock:
            raise RuntimeError("socket 未连接")
        self.sock.sendall(pack_frame(payload))

    def send_window_handle(self, window_id: int) -> None:
        self.window_id = window_id
        self.send_message({"msg": "ipc_user_info", "window": window_id})

    def write_jsonl(self, path: Path, row: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def write_raw(self, msg: dict[str, Any], payload_text: str | None = None) -> None:
        row = {
            "timestamp_utc": utc_now_iso(),
            "monotonic_ms": self.mono_ms(),
            "direction": "in",
            "msg": msg.get("msg"),
            "raw": msg,
        }
        if self.save_payload_text and payload_text is not None:
            row["payload_text"] = payload_text
        self.write_jsonl(self.raw_log, row)

    def log_decode_error(self, payload_text: str, err: Exception) -> None:
        self.write_jsonl(self.decode_err_log, {
            "timestamp_utc": utc_now_iso(),
            "monotonic_ms": self.mono_ms(),
            "error": str(err),
            "payload_text": payload_text,
        })

    def get_value(self, data: dict[str, Any], keys: list[str]) -> Any:
        for k in keys:
            if k in data:
                return data[k]
        return None

    def parse_gyro_from_algorithm(self, message: dict[str, Any], algorithm_name: str | None, data: Any) -> GyroSample | None:
        if not isinstance(data, dict):
            return None
        has_gyro_hint = any(k in data for k in ["focus_x", "focus_y", "gyroscope_x", "gyroscope_y", "gyroscope_z", "gyroscopeX", "gyroscopeY", "gyroscopeZ", "gyro_x", "gyro_y", "gyro_z"])
        if (algorithm_name not in {"gyroscope", "gyro"}) and not has_gyro_hint:
            return None
        return GyroSample(
            timestamp_utc=utc_now_iso(), monotonic_ms=self.mono_ms(), session_id=self.session_id,
            source_msg="ipc_algorithm_test", algorithm_name=algorithm_name,
            focus_x=self.get_value(data, ["focus_x", "focusX"]),
            focus_y=self.get_value(data, ["focus_y", "focusY"]),
            focus_area_x=self.get_value(data, ["focus_area_x", "focusAreaX"]),
            focus_area_y=self.get_value(data, ["focus_area_y", "focusAreaY"]),
            focus_area_width=self.get_value(data, ["focus_area_width", "focusAreaWidth"]),
            focus_area_height=self.get_value(data, ["focus_area_height", "focusAreaHeight"]),
            gyro_x=self.get_value(data, ["gyroscope_x", "gyroscopeX", "gyro_x", "gyroX"]),
            gyro_y=self.get_value(data, ["gyroscope_y", "gyroscopeY", "gyro_y", "gyroY"]),
            gyro_z=self.get_value(data, ["gyroscope_z", "gyroscopeZ", "gyro_z", "gyroZ"]),
            valid=True, raw=message,
        )

    def parse_gyro_from_device_msg(self, message: dict[str, Any]) -> GyroSample:
        return GyroSample(
            timestamp_utc=utc_now_iso(), monotonic_ms=self.mono_ms(), session_id=self.session_id,
            source_msg="ipc_device_gyroscope", algorithm_name="ipc_device_gyroscope",
            focus_x=None, focus_y=None, focus_area_x=None, focus_area_y=None, focus_area_width=None, focus_area_height=None,
            gyro_x=message.get("gyroscopeX"), gyro_y=message.get("gyroscopeY"), gyro_z=message.get("gyroscopeZ"),
            valid=True, raw=message,
        )

    def record_attention(self, algorithm_name: str, attention: int) -> None:
        self.write_jsonl(self.sensor_log, {
            "timestamp_utc": utc_now_iso(), "monotonic_ms": self.mono_ms(), "session_id": self.session_id,
            "event_type": "attention_sample", "algorithm_name": algorithm_name, "attention": attention, "valid": True,
        })

    def record_gyro(self, sample: GyroSample) -> None:
        event = asdict(sample)
        event["event_type"] = "gyro_sample"
        self.write_jsonl(self.sensor_log, event)

    def handle_message(self, message: dict[str, Any], payload_text: str) -> None:
        self.last_msg = message.get("msg")
        self.write_raw(message, payload_text)
        if self.dump_raw and self.raw_dump_count < self.raw_limit:
            print(json.dumps(message, ensure_ascii=False))
            self.raw_dump_count += 1

        msg = message.get("msg")
        if msg == "ipc_user_info":
            self.layout_type = message.get("layout_type")
            if self.layout_type == 1 and self.window_id is None:
                print("当前为分屏布局，但控制台程序没有窗口句柄。后续 GUI 程序需要调用 send_window_handle(window_id) 完成嵌入。")
        elif msg == "ipc_algorithm_test":
            algorithm_name = message.get("algorithm_name") or message.get("algorithm_name:")
            self.last_algorithm_name = algorithm_name
            result_args = message.get("result_args")
            if not isinstance(result_args, dict):
                result_args = {}
            data = result_args.get("data")
            if self.verbose:
                print(f"算法输出: algorithm_name={algorithm_name}, data_type={type(data).__name__}, data={data}")
            if algorithm_name == "attention":
                try:
                    att = int(data)
                    self.attention_value = att
                    self.attention_valid = True
                    self.attention_ts_ms = self.mono_ms()
                    self.record_attention(algorithm_name, att)
                    if self.print_attention:
                        print(f"注意力值: {att}")
                except (TypeError, ValueError):
                    self.attention_valid = False
            gyro_sample = self.parse_gyro_from_algorithm(message, algorithm_name, data)
            if gyro_sample:
                self.focus_x, self.focus_y = gyro_sample.focus_x, gyro_sample.focus_y
                self.gyro_x, self.gyro_y, self.gyro_z = gyro_sample.gyro_x, gyro_sample.gyro_y, gyro_sample.gyro_z
                self.gyro_valid = True
                self.gyro_ts_ms = self.mono_ms()
                self.record_gyro(gyro_sample)
        elif msg == "ipc_device_gyroscope":
            gyro_sample = self.parse_gyro_from_device_msg(message)
            self.gyro_x, self.gyro_y, self.gyro_z = gyro_sample.gyro_x, gyro_sample.gyro_y, gyro_sample.gyro_z
            self.gyro_valid = True
            self.gyro_ts_ms = self.mono_ms()
            self.record_gyro(gyro_sample)
        elif msg == "ipc_device_info":
            self.device_connected = message.get("device_connected", self.device_connected)
            self.device_wear = message.get("device_wear", self.device_wear)
            self.battery = message.get("battery", self.battery)
            self.sample_rate = message.get("sample_rate", self.sample_rate)
            self.blink_state = message.get("blink_state", self.blink_state)
        elif msg == "ipc_exit":
            print("收到 ipc_exit，准备安全退出")
            self.running = False

    def get_snapshot(self) -> dict[str, Any]:
        now_ms = self.mono_ms()
        return {
            "connected": self.connected,
            "layout_type": self.layout_type,
            "last_msg": self.last_msg,
            "last_algorithm_name": self.last_algorithm_name,
            "attention_value": self.attention_value,
            "attention_valid": self.attention_valid,
            "attention_age_ms": None if self.attention_ts_ms is None else now_ms - self.attention_ts_ms,
            "focus_x": self.focus_x,
            "focus_y": self.focus_y,
            "gyro_x": self.gyro_x,
            "gyro_y": self.gyro_y,
            "gyro_z": self.gyro_z,
            "gyro_valid": self.gyro_valid,
            "gyro_age_ms": None if self.gyro_ts_ms is None else now_ms - self.gyro_ts_ms,
            "blink_state": self.blink_state,
            "device_connected": self.device_connected,
            "device_wear": self.device_wear,
            "battery": self.battery,
            "sample_rate": self.sample_rate,
        }

    def recv_loop(self) -> None:
        if not self.sock:
            raise RuntimeError("socket 未连接")
        while self.running:
            data = self.sock.recv(4096)
            if not data:
                print("连接已断开，退出接收循环")
                break
            try:
                for msg, text in self.parser.feed(data):
                    self.handle_message(msg, text)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                payload_text = data.decode("utf-8", errors="replace")
                self.log_decode_error(payload_text, exc)
                print(f"解析 JSON 失败: {exc}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="RELIC IPC client")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--print", dest="print_attention", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--dump-raw", action="store_true")
    p.add_argument("--raw-limit", type=int, default=20)
    p.add_argument("--save-payload-text", action="store_true")
    return p


def main() -> int:
    args = build_parser().parse_args()
    client = RelicClient(args.host, args.port, args.print_attention, args.verbose, args.dump_raw, args.raw_limit, args.save_payload_text)
    try:
        client.connect()
        client.recv_loop()
        return 0
    except KeyboardInterrupt:
        print("收到 Ctrl+C，正在安全关闭")
        return 0
    except OSError as exc:
        print(f"连接失败 {args.host}:{args.port}: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
