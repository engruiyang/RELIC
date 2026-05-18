from pathlib import Path


def test_task25c_game_canvas_trace_lock_asset_pack_tokens() -> None:
    text = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    for token in [
        "targetAssetKey",
        "targetAssetDescriptor",
        "targetImageSource",
        "targetFallbackShape",
        "isTargetImageAvailable",
        "asset_key",
        "fallback_shape",
        "Image {",
        "TASK25C GameCanvas consumes TraceLock visual asset_key/style_key tokens",
    ]:
        assert token in text
    for forbidden in ["subprocess", "Popen", "os.system", "AssetManager", "ThemeManager", "LayoutManager"]:
        assert forbidden not in text


def test_task25c_manifest_declares_trace_lock_visual_slots_without_binary_assets() -> None:
    manifest = Path("assets/manifest.json").read_text(encoding="utf-8")
    for token in [
        "tracelock.target.marked_trace",
        "tracelock.target.noise_trace",
        "tracelock.focus_zone.default",
        "tracelock.progress_ring.default",
        "tracelock.timer_bar.default",
    ]:
        assert token in manifest
    for suffix in [".png", ".jpg", ".jpeg", ".svg", ".ttf", ".otf", ".wav", ".mp3"]:
        assert suffix not in manifest.lower()


def test_task25c_trace_lock_json_controls_canvas_and_fallback_shapes() -> None:
    text = Path("assets/packs/default/games/trace_lock.json").read_text(encoding="utf-8")
    for token in [
        "canvas",
        "background",
        "target",
        "marked_trace",
        "noise_trace",
        "asset_key",
        "fallback_shape",
        "progress_ring",
        "timer_bar",
        "hud",
    ]:
        assert token in text


def test_task25c_default_theme_uses_high_contrast_debug_readability() -> None:
    text = Path("assets/packs/default/theme.json").read_text(encoding="utf-8")
    for token in [
        "#F8FAFC",
        "#FFFFFF",
        "#0F172A",
        "#475569",
    ]:
        assert token in text
