from __future__ import annotations

import json
from pathlib import Path


def _json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_tracelock_audio_resource_slots_and_config_are_present() -> None:
    manifest = _json("assets/manifest.json")
    common = manifest.get("common_assets") or {}
    for key in [
        "audio.ui.click",
        "audio.tracelock.hit",
        "audio.tracelock.miss",
        "audio.tracelock.combo",
        "audio.tracelock.music.loop",
        "audio.tracelock.ambient.loop",
    ]:
        assert key in common
        assert common[key].get("type") == "audio"
        assert common[key].get("style_key") == key
        assert str(common[key].get("url") or "").startswith("packs/default/audio/")

    pack = _json("assets/packs/default/pack.json")
    audio_group = pack.get("asset_slot_groups", {}).get("audio", [])
    assert "audio.tracelock.combo" in audio_group

    game_cfg = _json("assets/packs/default/games/trace_lock.json")
    audio_cfg = game_cfg.get("audio") or {}
    assert audio_cfg.get("music_key") == "audio.tracelock.music.loop"
    assert audio_cfg.get("ambient_key") == "audio.tracelock.ambient.loop"
    assert audio_cfg.get("hit_key") == "audio.tracelock.hit"
    assert audio_cfg.get("miss_key") == "audio.tracelock.miss"
    assert audio_cfg.get("combo_key") == "audio.tracelock.combo"
    assert audio_cfg.get("ui_click_key") == "audio.ui.click"
    assert audio_cfg.get("playback_enabled") is False
    assert audio_cfg.get("music_enabled") is False
    assert audio_cfg.get("sfx_enabled") is False


def test_tracelock_audio_controller_uses_qtmultimedia_outside_game_canvas() -> None:
    controller = Path("ui_qml/components/TraceLockAudioController.qml").read_text(encoding="utf-8")
    for token in [
        "import QtMultimedia",
        "TraceLockAudioController",
        "MediaPlayer",
        "AudioOutput",
        "SoundEffect",
        "audio.tracelock.music.loop",
        "audio.tracelock.ambient.loop",
        "audio.tracelock.hit",
        "audio.tracelock.miss",
        "audio.tracelock.combo",
        "audio.ui.click",
        "playSfx",
        "updateMusicState",
        "consumeVisualEvents",
        "visualEventAudioKey",
        "playableUrl",
    ]:
        assert token in controller

    minimal = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    for token in [
        "TraceLockAudioController {",
        "id: traceLockAudioController",
        "playbackEnabled: root.traceLockAudioPlaybackEnabled",
        "musicKey: root.traceLockMusicKey",
        "hitKey: root.traceLockHitKey",
        "sfxVolume: root.traceLockSfxVolume",
    ]:
        assert token in minimal
    assert "Loader" not in minimal
    assert "traceLockAudioControllerLoader" not in minimal

    game_canvas = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    assert "QtMultimedia" not in game_canvas
    assert "MediaPlayer" not in game_canvas
    assert "SoundEffect" not in game_canvas


def test_tracelock_demo_audio_files_are_replaceable_placeholders() -> None:
    manifest = _json("assets/manifest.json")
    common = manifest.get("common_assets") or {}
    for key in [
        "audio.ui.click",
        "audio.tracelock.hit",
        "audio.tracelock.miss",
        "audio.tracelock.combo",
        "audio.tracelock.music.loop",
        "audio.tracelock.ambient.loop",
    ]:
        rel = common[key]["url"]
        path = Path("assets") / rel
        assert path.exists(), f"{key} placeholder missing: {path}"
        assert path.suffix.lower() == ".wav"
        assert path.stat().st_size > 44
