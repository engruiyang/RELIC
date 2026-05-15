from __future__ import annotations

import json
import re
from pathlib import Path


def test_trace_lock_visual_contract() -> None:
    design = Path("docs/games/trace_lock_design.md")
    manifest = Path("assets/games/trace_lock/visual_manifest.json")
    readme = Path("assets/games/trace_lock/README.md")

    assert design.exists()
    assert manifest.exists()
    assert readme.exists()

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["game_id"] == "trace_lock"
    assert data["display_name"] == "TraceLock Protocol"
    assert data["subtitle"] == "Data Trace Tracking Protocol"
    assert data["vendor"] == "Qilin Logic"

    assets = data["assets"]
    for k in [
        "tracelock.target.marked_trace",
        "tracelock.target.burst_trace",
        "tracelock.target.unstable_trace",
        "tracelock.focus_zone.default",
        "tracelock.progress_ring.default",
        "tracelock.timer.round",
    ]:
        assert k in assets

    effects = data["effects"]
    for k in [
        "tracelock.effect.trace_seal",
        "tracelock.effect.lock_failed",
        "tracelock.effect.trace_drop",
    ]:
        assert k in effects

    assert all(v.get("url") is None for v in assets.values())
    assert all(v.get("url") is None for v in effects.values())

    raw_manifest = manifest.read_text(encoding="utf-8")
    for forbidden in [
        ".png",
        ".webp",
        ".svg",
        "Cyberpunk 2077",
        "Night City",
        "CD Projekt",
        "PlatformReporter",
        "ipc_mouse_data",
        "SessionManager",
        "SQLite",
        "DataCenter",
        "GameEvent",
        "GameInputEvent",
    ]:
        assert forbidden not in raw_manifest

    assert re.search(r"\bFI\b", raw_manifest) is None
    assert re.search(r"\bSQI\b", raw_manifest) is None

    for entity in ["target", "focus_zone", "progress_ring", "timer_bar"]:
        assert entity in data["supported_entities"]

    for state in ["active", "locked", "failed", "expired", "warning", "disabled"]:
        assert state in data["supported_visual_states"]

    design_text = design.read_text(encoding="utf-8")
    assert "禁止事项" in design_text
    assert "asset_key / style_key / effect_key" in design_text
    assert "小游戏不得直接读取素材文件" in design_text
    assert "RELIC Core" in design_text
    assert "Qilin Logic Trace Predict" in design_text

    readme_text = readme.read_text(encoding="utf-8")
    assert "不要让 QML 直接读取" in readme_text
    assert "资源由 Python `ResourceManager` 读取" in readme_text
