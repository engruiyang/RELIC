#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone RELIC IPC parser for HNNK TCP frames."""

from __future__ import annotations

import argparse
import json
import socket
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MSG_CONNECTED = "\u5df2\u8fde\u63a5\u79d1\u521b\u5e73\u53f0 {host}:{port}"
MSG_CONNECT_FAILED = "\u8fde\u63a5\u5931\u8d25 {host}:{port}: {err}"
MSG_JSON_FAIL = "\u89e3\u6790 JSON \u5931\u8d25: {err}"
MSG_NON_DICT = "\u8b66\u544a: \u6536\u5230\u975e dict JSON\uff0c\u5df2\u8df3\u8fc7"
MSG_RECV_FAILED = "\u63a5\u6536\u6570\u636e\u5931\u8d25: {err}"
MSG_DISCONNECTED = "\u8fde\u63a5\u5df2\u65ad\u5f00\uff0c\u9000\u51fa\u63a5\u6536\u5faa\u73af"
MSG_EXIT = "\u6536\u5230 ipc_exit\uff0c\u51c6\u5907\u5b89\u5168\u9000\u51fa"
MSG_CTRL_C = "\u6536\u5230 Ctrl+C\uff0c\u6b63\u5728\u5b89\u5168\u5173\u95ed"
MSG_RECV = "\u6536\u5230\u6d88\u606f: {msg}"
MSG_LAYOUT = "layout_type: {layout}"
MSG_ATTENTION = "\u6ce8\u610f\u529b\u503c: {value}"
MSG_ATTENTION_BAD = "\u8b66\u544a: \u65e0\u6cd5\u5c06 attention data \u8f6c\u6362\u4e3a int: {data}"
MSG_VISIBLE = "set_visible: {visible}"


def pack_frame(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return struct.pack(">I", len(body)) + body


class FrameParser:
    def __init__(self) -> None:
        self._buffer = bytearray()

    def feed(self, data: bytes) -> list[dict[str, Any]]:
        self._buffer.extend(data)
        messages: list[dict[str, Any]] = []

        while True:
            if len(self._buffer) < 4:
                break
            payload_len = struct.unpack(">I", self._buffer[:4])[0]
            total_len = 4 + payload_len
            if len(self._buffer) < total_len:
                break

            payload_bytes = bytes(self._buffer[4:total_len])
            del self._buffer[:total_len]

            try:
                obj = json.loads(payload_bytes.decode("utf-8"))
                if isinstance(obj, dict):
                    messages.append(obj)
                else:
                    print(MSG_NON_DICT, file=sys.stderr)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                print(MSG_JSON_FAIL.format(err=exc), file=sys.stderr)

        return messages


class HnnkIpcClient:
    def __init__(self, host: str, port: int, log_path: str, verbose: bool = False) -> None:
        self.host = host
        self.port = port
        self.verbose = verbose
        self.log_path = Path(log_path)
        self.sock: socket.socket | None = None
        self.parser = FrameParser()
        self._running = False

    def connect(self) -> None:
        try:
            self.sock = socket.create_connection((self.host, self.port))
            self._running = True
            print(MSG_CONNECTED.format(host=self.host, port=self.port))
        except OSError as exc:
            print(MSG_CONNECT_FAILED.format(host=self.host, port=self.port, err=exc), file=sys.stderr)
            raise

    def close(self) -> None:
        self._running = False
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.sock.close()
            self.sock = None

    def send_message(self, payload: dict[str, Any]) -> None:
        if self.sock is None:
            raise RuntimeError("socket not connected")
        self.sock.sendall(pack_frame(payload))

    def write_log(self, message: dict[str, Any], raw: str) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "msg": message.get("msg"),
            "raw": raw,
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def handle_message(self, message: dict[str, Any]) -> None:
        msg_name = message.get("msg")
        if self.verbose:
            print(MSG_RECV.format(msg=msg_name))

        if msg_name == "ipc_user_info":
            if self.verbose:
                print(MSG_LAYOUT.format(layout=message.get("layout_type")))
        elif msg_name == "ipc_algorithm_test":
            algorithm_name = message.get("algorithm_name")
            result_args = message.get("result_args") or {}
            if algorithm_name == "attention":
                data = result_args.get("data")
                try:
                    value = int(data)
                    if self.verbose:
                        print(MSG_ATTENTION.format(value=value))
                except (TypeError, ValueError):
                    print(MSG_ATTENTION_BAD.format(data=data), file=sys.stderr)
        elif msg_name == "ipc_set_visible":
            if self.verbose:
                print(MSG_VISIBLE.format(visible=message.get("visible")))
        elif msg_name == "ipc_exit":
            print(MSG_EXIT)
            self._running = False

    def recv_loop(self) -> None:
        if self.sock is None:
            raise RuntimeError("socket not connected")

        while self._running:
            try:
                chunk = self.sock.recv(4096)
            except OSError as exc:
                print(MSG_RECV_FAILED.format(err=exc), file=sys.stderr)
                break

            if not chunk:
                print(MSG_DISCONNECTED)
                break

            for msg in self.parser.feed(chunk):
                self.write_log(msg, json.dumps(msg, ensure_ascii=False))
                self.handle_message(msg)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RELIC HNNK IPC standalone parser")
    parser.add_argument("--host", default="127.0.0.1", help="TCP host, default 127.0.0.1")
    parser.add_argument("--port", type=int, default=8000, help="TCP port, default 8000")
    parser.add_argument("--print", dest="verbose", action="store_true", help="print received messages")
    parser.add_argument("--log", default="logs/ipc_raw.jsonl", help="log path, default logs/ipc_raw.jsonl")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    client = HnnkIpcClient(args.host, args.port, args.log, args.verbose)
    try:
        client.connect()
        client.recv_loop()
        return 0
    except OSError:
        return 1
    except KeyboardInterrupt:
        print(MSG_CTRL_C)
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
