#!/usr/bin/env python3

"""RELIC 独立通信解析程序。

连接 HNNK/科创平台 TCP 端口，按 4 字节大端长度头 + UTF-8 JSON 负载解析 IPC 帧，
并将原始消息写入 JSONL 日志。
"""


from __future__ import annotations

import argparse
import json
import socket
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def pack_frame(payload: dict[str, Any]) -> bytes:
    """将 dict 打包为官方 IPC 帧格式。"""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    header = struct.pack(">I", len(body))
    return header + body


class FrameParser:
    """处理 TCP 半包/粘包的帧解析器。"""

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
                payload_text = payload_bytes.decode("utf-8")
                obj = json.loads(payload_text)
                if isinstance(obj, dict):
                    messages.append(obj)
                else:
                    print("警告: 收到非 dict JSON，已跳过", file=sys.stderr)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                print(f"解析 JSON 失败: {exc}", file=sys.stderr)

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
            print(f"已连接科创平台 {self.host}:{self.port}")
        except OSError as exc:
            print(f"连接失败 {self.host}:{self.port}: {exc}", file=sys.stderr)
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
            raise RuntimeError("socket 未连接")
        frame = pack_frame(payload)
        self.sock.sendall(frame)

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
            print(f"收到消息: {msg_name}")

        if msg_name == "ipc_user_info":
            layout_type = message.get("layout_type")
            if self.verbose:
                print(f"layout_type: {layout_type}")

        elif msg_name == "ipc_algorithm_test":
            algorithm_name = message.get("algorithm_name")
            result_args = message.get("result_args") or {}
            data = result_args.get("data")
            if algorithm_name == "attention":
                try:
                    attention = int(data)
                    if self.verbose:
                        print(f"注意力值: {attention}")
                except (TypeError, ValueError):
                    print(f"警告: 无法将 attention data 转换为 int: {data}", file=sys.stderr)

        elif msg_name == "ipc_set_visible":
            if self.verbose:
                print(f"set_visible: {message.get('visible')}")

        elif msg_name == "ipc_exit":
            print("收到 ipc_exit，准备安全退出")
            self._running = False

    def recv_loop(self) -> None:
        if self.sock is None:
            raise RuntimeError("socket 未连接")

        while self._running:
            try:
                chunk = self.sock.recv(4096)
            except OSError as exc:
                print(f"接收数据失败: {exc}", file=sys.stderr)
                break

            if not chunk:
                print("连接已断开，退出接收循环")
                break

            messages = self.parser.feed(chunk)
            for msg in messages:
                raw = json.dumps(msg, ensure_ascii=False)
                self.write_log(msg, raw)
                self.handle_message(msg)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RELIC HNNK IPC 独立通信解析程序")
    parser.add_argument("--host", default="127.0.0.1", help="TCP 主机地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=8000, help="TCP 端口，默认 8000")
    parser.add_argument("--print", dest="verbose", action="store_true", help="打印收到的消息")
    parser.add_argument("--log", default="logs/ipc_raw.jsonl", help="日志路径，默认 logs/ipc_raw.jsonl")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    client = HnnkIpcClient(host=args.host, port=args.port, log_path=args.log, verbose=args.verbose)

    try:
        client.connect()
        client.recv_loop()
        return 0
    except OSError:
        return 1
    except KeyboardInterrupt:
        print("收到 Ctrl+C，正在安全关闭")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
