from pathlib import Path
import json
import re


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_user_actions_card_is_removed_from_user_desktop_config() -> None:
    data = json.loads(_read("assets/layouts/task26_examples/user_page.desktop_demo.json"))
    card_ids = [card.get("id") for card in data.get("cards", [])]
    assert "user_actions_card" not in card_ids
    assert "user_credentials_card" in card_ids
    assert "user_selector_card" in card_ids
    assert "user_profile_popup_card" in card_ids


def test_user_desktop_config_has_no_card_overlap_after_action_cleanup() -> None:
    data = json.loads(_read("assets/layouts/task26_examples/user_page.desktop_demo.json"))
    rects = []
    for card in data.get("cards", []):
        pos = card["position"]
        rects.append((card["id"], pos["col"], pos["row"], pos["col"] + pos["col_span"] - 1, pos["row"] + pos["row_span"] - 1))
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            overlap = not (a[3] < b[1] or b[3] < a[1] or a[4] < b[2] or b[4] < a[2])
            assert not overlap, f"{a} overlaps {b}"


def test_profile_popup_reads_action_result_and_calibration_fields() -> None:
    text = _read("ui_qml/components/DesktopLayoutCardPreview.qml")
    assert "lastProfileActionRaw" in text
    assert "function profileValue" in text
    assert "extractJsonBool" in text
    assert "Attention baseline:" in text
    assert "Calibration usable:" in text
    assert "Gyro noise RMS:" in text
    assert 'actionId === "user.show_profile"' in text


def test_user_show_profile_action_returns_calibration_detail() -> None:
    text = _read("gui/gui_facade.py")
    block = re.search(r'elif action_id == "user\.show_profile":(?P<body>.*?)elif action_id == "calibration\.status":', text, re.S)
    assert block, "user.show_profile branch not found"
    body = block.group("body")
    assert "_fetch_profile_summary" in body
    assert "_fetch_calibration_status" in body
    assert "attention_baseline" in body
    assert "gyro_noise_rms" in body
    assert '"calibration"' in body
