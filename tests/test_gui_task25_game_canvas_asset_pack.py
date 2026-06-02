from pathlib import Path

def test_training_page_passes_render_resources_obj() -> None:
    text = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    assert 'TrainingPage {' in text
    assert 'renderResourcesObj: root.renderResourcesObj' in text


def test_trace_lock_replaceable_asset_slots_exposed_in_render_resources() -> None:
    from core.resource_managers import build_render_resource_bundle

    bundle = build_render_resource_bundle(game_id="trace_lock")
    assets = bundle.get("assets") or {}
    styles = bundle.get("styles") or {}
    for key in [
        "tracelock.background.default",
        "tracelock.background.grid",
        "tracelock.target.marked_trace",
        "tracelock.target.burst_trace",
        "tracelock.target.unstable_trace",
        "tracelock.progress_ring.default",
        "tracelock.timer_bar.default",
        "tracelock.effect.trace_seal",
        "tracelock.effect.lock_failed",
        "tracelock.effect.trace_drop",
        "tracelock.effect.combo_popup",
        "tracelock.effect.local_ripple",
    ]:
        assert key in assets
        assert assets[key].get("fallback_shape")
        style_key = assets[key].get("style_key")
        if style_key:
            assert style_key in styles


def test_game_canvas_consumes_trace_lock_asset_slots_with_fallbacks() -> None:
    text = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")
    for token in [
        "backgroundImageSource",
        "targetImageSource",
        "targetFallbackShape",
        "rowImageSource",
        "effectImageSource",
        "isEffectImageAvailable",
        "renderResourceStyle",
        "fallback_shape",
        "tracelock.effect.local_ripple",
    ]:
        assert token in text
