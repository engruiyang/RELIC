from pathlib import Path

COMPONENT_DIR = Path("ui_qml/components")

TASK26_COMPONENTS = [
    "DesignCard.qml",
    "ConfigTextWidget.qml",
    "ConfigMetricWidget.qml",
    "ConfigButtonWidget.qml",
    "CardHostPreview.qml",
]

BANNED_TOKENS = [
    "Loader",
    "Repeater",
    "Timer",
    "subprocess",
]


def _read_component(name: str) -> str:
    path = COMPONENT_DIR / name
    assert path.exists(), path
    return path.read_text(encoding="utf-8")


def test_task26_card_components_exist() -> None:
    for name in TASK26_COMPONENTS:
        assert (COMPONENT_DIR / name).exists(), name


def test_task26_card_components_do_not_use_high_risk_runtime_structures() -> None:
    for name in TASK26_COMPONENTS:
        text = _read_component(name)
        for token in BANNED_TOKENS:
            assert token not in text, f"{name} contains banned token {token}"


def test_task26_design_card_contract_tokens() -> None:
    text = _read_component("DesignCard.qml")
    required = [
        "cardTitle",
        "cardSubtitle",
        "backgroundColor",
        "backgroundOpacity",
        "backgroundImage",
        "borderColor",
        "borderWidth",
        "radiusValue",
        "paddingValue",
        "shapeType",
        "contentData",
    ]
    for token in required:
        assert token in text


def test_task26_config_button_contract_tokens() -> None:
    text = _read_component("ConfigButtonWidget.qml")
    required = [
        "guiBridge",
        "label",
        "actionId",
        "argsJson",
        "variant",
        "confirmEnabled",
        "confirmMessage",
        "required",
        "actionRequested",
        "invokeAction",
    ]
    for token in required:
        assert token in text


def test_task26_cardhost_preview_contract_tokens() -> None:
    text = _read_component("CardHostPreview.qml")
    required = [
        "Runtime I/O",
        "Quick Actions",
        "Session",
        "RELIC Desktop Card System",
        "app.refresh_now",
        "live.safe_stop",
    ]
    for token in required:
        assert token in text
