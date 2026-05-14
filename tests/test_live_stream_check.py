import json
from pathlib import Path

from ui_cli.run_live_stream_check import run_live_stream_check


class FakeGateway:
    def __init__(self, frames: list[list[dict]], fail_on_start: bool = False):
        self.frames = frames
        self.i = 0
        self.started = False
        self.fail_on_start = fail_on_start

    def start(self) -> None:
        if self.fail_on_start:
            raise RuntimeError("connect fail")
        self.started = True

    def stop(self) -> None:
        self.started = False

    def health(self) -> dict:
        return {"connected": self.started, "alive": self.started}

    def poll_raw_events(self, now_ms: int) -> list[dict]:
        _ = now_ms
        if self.i >= len(self.frames):
            self.i += 1
            return []
        out = self.frames[self.i]
        self.i += 1
        return out


def test_live_stream_check_normal_attention_gyro() -> None:
    frames = [
        [{"type": "device_status", "connected": True}, {"type": "stream_status", "alive": True, "active": True}],
        [{"type": "attention", "value": 61}, {"type": "gyroscope", "x": 1, "y": 2, "z": 3}],
        [{"type": "gyroscope", "x": 2, "y": 3, "z": 4}],
        [{"type": "attention", "value": 63}, {"type": "gyroscope", "x": 3, "y": 4, "z": 5}],
    ]
    s = run_live_stream_check("127.0.0.1", 8000, 1, "data/relic_local.db", "logs/live_stream_checks", tick_ms=20, gateway=FakeGateway(frames))
    assert s["decoded_attention_count"] >= 2
    assert s["decoded_gyro_count"] >= 3
    assert s["last_attention"] is not None
    assert s["last_gyro"]["x"] is not None
    assert "final_attention_fresh" in s
    assert "final_gyro_fresh" in s
    assert isinstance(s["current_warning_flags"], list)
    assert isinstance(s["historical_warning_flags"], list)


def test_live_stream_check_attention_stale_with_gyro_only() -> None:
    frames = [[{"type": "device_status", "connected": True}, {"type": "stream_status", "alive": True, "active": True}]] + [
        [{"type": "gyroscope", "x": 1, "y": 2, "z": 3}] for _ in range(10)
    ]
    s = run_live_stream_check("127.0.0.1", 8000, 1, "data/relic_local.db", "logs/live_stream_checks", tick_ms=20, gateway=FakeGateway(frames))
    assert s["decoded_attention_count"] == 0
    assert s["decoded_gyro_count"] > 0
    assert "attention_stale" in s["warning_flags"] or "attention_missing" in s["warning_flags"]


def test_live_stream_check_no_data() -> None:
    s = run_live_stream_check("127.0.0.1", 8000, 1, "data/relic_local.db", "logs/live_stream_checks", tick_ms=20, gateway=FakeGateway([]))
    assert s["raw_message_count"] == 0
    assert "no_data" in s["error_flags"]


def test_live_stream_check_json_serializable_and_connect_fail() -> None:
    s = run_live_stream_check("127.0.0.1", 8000, 1, "data/relic_local.db", "logs/live_stream_checks", tick_ms=20, gateway=FakeGateway([], fail_on_start=True))
    dumped = json.dumps(s, ensure_ascii=False)
    assert dumped
    assert "connect_failed" in s["error_flags"]


def test_output_dir_creates_summary_file_and_path(tmp_path: Path) -> None:
    frames = [
        [{"type": "device_status", "connected": True}, {"type": "stream_status", "alive": True, "active": True}],
        [{"type": "attention", "value": 68}, {"type": "gyroscope", "x": 10, "y": 11, "z": 12}],
    ]
    s = run_live_stream_check("127.0.0.1", 8000, 1, "data/relic_local.db", str(tmp_path), tick_ms=20, gateway=FakeGateway(frames))
    assert s["output_log_path"] is not None
    output_file = Path(s["output_log_path"])
    assert output_file.exists()
    assert output_file.parent == tmp_path
    assert output_file.read_text(encoding="utf-8")
    assert "attention_missing" not in s["current_warning_flags"]
    assert "gyro_missing" not in s["current_warning_flags"]
