import json
from pathlib import Path


MANIFEST_PATH = Path("assets/games/shard_lock/visual_manifest.json")
DESIGN_DOC_PATH = Path("docs/games/shard_lock_design.md")


REQUIRED_ASSETS = {
    "shardlock.target.primary",
    "shardlock.target.burst",
    "shardlock.target.unstable",
    "shardlock.focus_zone.default",
    "shardlock.progress_ring.default",
    "shardlock.timer.round",
}

REQUIRED_EFFECTS = {
    "shardlock.effect.lock_success",
    "shardlock.effect.lock_failed",
}

REQUIRED_SUPPORTED_ENTITIES = {
    "target",
    "focus_zone",
    "progress_ring",
    "timer_bar",
}

FORBIDDEN_PATTERNS = [
    "PlatformReporter",
    "ipc_mouse_data",
    "SessionManager",
    "SQLite",
    "DataCenter",
    "GameEvent",
    "GameInputEvent",
    "FI",
    "SQI",
    ".png",
    ".webp",
    ".svg",
]


def test_manifest_exists_and_is_valid_json() -> None:
    assert MANIFEST_PATH.exists()
    raw = MANIFEST_PATH.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert isinstance(parsed, dict)


def test_manifest_basic_contract() -> None:
    parsed = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert parsed["game_id"] == "shard_lock"

    assets = parsed.get("assets") or {}
    effects = parsed.get("effects") or {}
    supported_entities = set(parsed.get("supported_entities") or [])

    assert REQUIRED_ASSETS.issubset(set(assets.keys()))
    assert REQUIRED_EFFECTS.issubset(set(effects.keys()))
    assert REQUIRED_SUPPORTED_ENTITIES.issubset(supported_entities)


def test_manifest_asset_urls_are_null_in_first_release() -> None:
    parsed = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for _, desc in (parsed.get("assets") or {}).items():
        assert "url" in desc
        url = desc.get("url")
        assert url is None or (isinstance(url, str) and not url.startswith("/"))
        assert url is None


def test_manifest_not_polluted_with_platform_or_real_asset_paths() -> None:
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in text


def test_design_doc_exists_and_contains_rules() -> None:
    assert DESIGN_DOC_PATH.exists()
    text = DESIGN_DOC_PATH.read_text(encoding="utf-8")
    assert "禁止事项" in text
    assert "asset_key" in text
    assert "style_key" in text
    assert "effect_key" in text
    assert "不读取 assets/*.json" in text
    assert "小游戏" in text and "不读取素材文件" in text
