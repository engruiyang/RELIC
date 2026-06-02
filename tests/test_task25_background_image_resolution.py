from pathlib import Path


def test_design_background_resolves_layered_image_asset_key_and_manifest_url() -> None:
    text = Path("ui_qml/components/DesignBackground.qml").read_text(encoding="utf-8")

    assert 'typeof bg.image === "object"' in text
    assert 'root.value(image, "asset_key"' in text
    assert "return root.assetUrl(layer.asset_key)" in text
    assert 'Qt.resolvedUrl("../../assets/" + u)' in text
    assert "function imageOpacity()" in text
    assert 'root.value(layer, "opacity", 1.0)' in text


def test_design_background_supports_page_layered_schema_without_hiding_images() -> None:
    text = Path("ui_qml/components/DesignBackground.qml").read_text(encoding="utf-8")

    for token in [
        "bg.gradient",
        "bg.overlay",
        'root.value(image, "asset_key"',
        'root.value(image, "opacity"',
        'root.value(image, "fit"',
        'root.value(image, "position"',
        "Image {",
        "source: root.imageSource()",
        'visible: source !== ""',
        "asynchronous: true",
        "cache: false",
    ]:
        assert token in text


def test_game_canvas_uses_same_asset_url_resolution_for_trace_lock_images() -> None:
    text = Path("ui_qml/components/GameCanvas.qml").read_text(encoding="utf-8")

    assert "targetAssetKey" in text
    assert "targetImageSource" in text
    assert "targetFallbackShape" in text
    assert 'Qt.resolvedUrl("../../assets/" + u)' in text
    assert 'sendEvent("pointer_click"' in text
    for forbidden in ["subprocess", "Popen", "os.system"]:
        assert forbidden not in text


def test_pages_and_minimal_gui_pass_render_resource_background_tokens() -> None:
    page_files = [
        "ui_qml/pages/HomePage.qml",
        "ui_qml/pages/UserPage.qml",
        "ui_qml/pages/CalibrationPage.qml",
        "ui_qml/pages/TrainingPage.qml",
        "ui_qml/pages/ReportPage.qml",
        "ui_qml/pages/DiagnosticsPage.qml",
        "ui_qml/pages/DeveloperLabPage.qml",
    ]

    minimal = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    assert "renderResourcesObj = safeJsonParse(guiBridge.renderResourcesJson)" in minimal
    assert "DesignBackground {" in minimal
    assert "renderResourcesObj: root.renderResourcesObj" in minimal

    for path in page_files:
        text = Path(path).read_text(encoding="utf-8")
        assert "property var pageStyleObj" in text, path
        assert "property var renderResourcesObj" in text, path
        assert "DesignBackground {" in text, path
        assert "pageStyleObj" in text, path
        assert "renderResourcesObj:" in text, path
        for forbidden in ["subprocess", "Popen", "os.system"]:
            assert forbidden not in text, path
