from pathlib import Path
import json


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_panel_header_feedback_asset_pipelines_are_wired() -> None:
    minimal = _read("ui_qml/MinimalGui.qml")
    assert "renderResourcesObj" in minimal
    assert "designThemeObj" in minimal
    for page in ["HomePage", "TrainingPage", "UserPage", "CalibrationPage", "ReportPage", "DiagnosticsPage"]:
        text = _read(f"ui_qml/pages/{page}.qml")
        assert "Page Feedback" in text


def test_page_layout_jsons_have_cards_for_asset_skinning() -> None:
    for path in Path("assets/layouts/task26_examples").glob("*_page.desktop_demo.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data.get("cards"), list) and data["cards"]


def test_tracelock_manifest_has_replaceable_slots_and_null_url_fallbacks() -> None:
    manifest = json.loads(Path("assets/manifest.json").read_text(encoding="utf-8"))
    common = manifest.get("common_assets") or {}
    required = [
        "tracelock.background.default",
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
    ]
    for key in required:
        assert key in common
        desc = common[key]
        assert desc.get("task25e0_role") == "artist_replaceable_slot"
        assert desc.get("style_key")
        assert desc.get("fallback_shape")
