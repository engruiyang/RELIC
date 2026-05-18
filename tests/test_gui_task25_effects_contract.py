from pathlib import Path
import json


def test_task25d_trace_lock_effects_contract_fields() -> None:
    effects = json.loads(Path("assets/packs/default/effects/trace_lock_effects.json").read_text(encoding="utf-8"))
    for key in ["trace_seal", "lock_failed", "trace_drop", "combo_popup"]:
        assert key in effects
        effect = effects[key]
        for field in ["type", "duration_ms", "color", "radius", "scale_from", "scale_to", "opacity_from", "opacity_to"]:
            assert field in effect
    assert effects["trace_seal"]["particle_count"] >= 1
    assert effects["trace_seal"]["type"] in {"particle_burst", "burst", "pulse"}
    assert effects["lock_failed"]["type"] in {"flash", "shock"}
    assert effects["trace_drop"]["type"] in {"fade", "drop"}
    assert effects["combo_popup"]["type"] in {"popup", "float"}


def test_task25d_game_canvas_consumes_effect_styles_without_control_logic_changes() -> None:
    text = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    for token in [
        "effectStyle",
        "effectColor",
        "effectGlow",
        "effectDuration",
        "effectTypeName",
        "effectParticleCount",
        "effectScaleFrom",
        "effectScaleTo",
        "effectOpacityFrom",
        "effectOpacityTo",
        "particle_burst",
        "combo_popup",
        "trace_drop",
        "lock_failed",
        "NumberAnimation on scale",
        "NumberAnimation on opacity",
        "TASK25D effect_styles parameterize",
    ]:
        assert token in text
    assert "sendEvent(\"pointer_click\"" in text
    for forbidden in ["subprocess", "Popen", "os.system", "AssetManager", "ThemeManager", "LayoutManager"]:
        assert forbidden not in text


def test_task25b2h_page_feedback_panel_does_not_customize_native_background() -> None:
    text = Path("ui_qml/components/PageFeedbackPanel.qml").read_text(encoding="utf-8")
    assert "Page Feedback" in text
    assert "background:" not in text
    assert "GroupBox" not in text
    assert "Control" not in text
    assert "TASK25B-2H PageFeedbackPanel is self-painted" in text
