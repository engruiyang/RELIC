from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui.desktop_coverage import (  # noqa: E402
    collect_cards_fields_buttons_from_pages,
    load_pipeline_bindings,
    validate_action_ids,
    validate_pipeline_coverage,
    validate_safe_stop_accessible,
)
from gui.desktop_model import (  # noqa: E402
    build_home_card_slots,
    build_home_card_slots_injection_payload,
    build_home_render_model,
    build_training_card_slots,
    build_training_card_slots_injection_payload,
    build_training_contract_summary,
    build_training_render_model,
    diff_home_slot_injection_contract,
    expected_home_slot_injection_fields,
    expected_home_slot_qml_properties,
    validate_home_slot_injection_payload,
    validate_training_slot_injection_payload,
)
from gui.desktop_schema import (  # noqa: E402
    collect_action_ids_from_obj,
    collect_sources_from_obj,
    iter_task26_example_json,
    reject_script_like_values,
    validate_page_config,
    validate_source_roots,
)


def _extract_properties(text: str) -> set[str]:
    out: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("property "):
            parts = s.split()
            if len(parts) >= 3:
                out.add(parts[2].rstrip(":"))
    return out


def _extract_assignments(text: str) -> set[str]:
    out: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if ":" in s and not s.startswith("//"):
            left = s.split(":", 1)[0].strip()
            if left and left[0].isalpha():
                out.add(left)
    return out


def run(strict: bool = False, show_diff: bool = False) -> None:
    example_paths = iter_task26_example_json(ROOT)
    loaded: dict[str, dict] = {}
    for p in example_paths:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        reject_script_like_values(data)
        if isinstance(data, dict):
            loaded[p.name] = data

    desktop = loaded["desktop.example.json"]
    home_page = loaded["home_page.desktop_demo.json"]
    training_page = loaded["training_page.desktop_demo.json"]

    bindings = load_pipeline_bindings(ROOT / "assets/layouts/task26_examples/pipeline_ui_bindings.example.json")
    inventory = collect_cards_fields_buttons_from_pages([home_page, training_page], desktop)
    validate_pipeline_coverage(bindings, inventory, strict=strict)
    validate_safe_stop_accessible(inventory)

    validate_page_config(training_page)
    validate_action_ids(collect_action_ids_from_obj(training_page))
    validate_source_roots(collect_sources_from_obj(training_page))
    build_training_render_model(ROOT)
    training_summary = build_training_contract_summary(ROOT)
    required_training_cards = {
        "training_control_card",
        "session_card",
        "runtime_io_card",
        "calibration_status_card",
        "game_hud_card",
        "game_canvas_card",
        "diagnostics_summary_card",
    }
    missing_training_cards = sorted(required_training_cards - set(training_summary.get("required_card_ids", [])))
    if missing_training_cards:
        raise ValueError(f"training required cards missing: {missing_training_cards}")
    if training_summary.get("safe_stop_present") is not True:
        raise ValueError("training safe_stop_present must be true")
    if "placeholder" not in str(training_summary.get("game_canvas_card_status", "")):
        raise ValueError("training game_canvas_card placeholder missing")
    training_slots = build_training_card_slots(ROOT, max_slots=7)
    training_payload = build_training_card_slots_injection_payload(training_slots)
    validate_training_slot_injection_payload(training_payload)
    if "game_canvas_card" not in {str(slot.get("card_id", "")) for slot in training_slots}:
        raise ValueError("training slots missing game_canvas_card")
    training_slot_actions = {
        str(action_id)
        for slot in training_slots
        for action_id in (slot.get("action_ids") if isinstance(slot.get("action_ids"), list) else [])
    }
    if "live.safe_stop" not in training_slot_actions:
        raise ValueError("training slots missing live.safe_stop")

    training_slots_qml = (ROOT / "ui_qml/components/TrainingCardSlotsPreview.qml").read_text(encoding="utf-8")
    for card_id in required_training_cards:
        if card_id not in training_slots_qml:
            raise ValueError(f"TrainingCardSlotsPreview missing {card_id}")

    developer_lab_qml = (ROOT / "ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")
    if "task26_training_slots_payload" not in developer_lab_qml:
        raise ValueError("DeveloperLabPage missing task26_training_slots_payload")

    model = build_home_render_model(ROOT)
    slots = build_home_card_slots(model, max_slots=4)
    payload = build_home_card_slots_injection_payload(slots)
    validate_home_slot_injection_payload(payload)

    qml_component = (ROOT / "ui_qml/components/HomeCardSlotsPreview.qml").read_text(encoding="utf-8")
    qml_page = (ROOT / "ui_qml/pages/DeveloperLabPage.qml").read_text(encoding="utf-8")

    qml_props = _extract_properties(qml_component)
    expected_props = expected_home_slot_qml_properties()
    missing_props = sorted(expected_props - qml_props)
    if missing_props:
        raise ValueError(f"HomeCardSlotsPreview missing expected properties: {missing_props}")

    dev_props = _extract_assignments(qml_page)
    required_dev_props = {
        "slot1CardId",
        "slot2CardId",
        "slot3CardId",
        "slot4CardId",
        "slot1RectText",
        "slot1ActionIdsText",
        "slot1SourceRootsText",
        "slot1FirstWidgetLabelsText",
    }
    missing_required = sorted(required_dev_props - dev_props)
    if missing_required:
        raise ValueError(f"DeveloperLabPage missing required slot assignments: {missing_required}")

    diff = diff_home_slot_injection_contract(
        payload_fields=expected_home_slot_injection_fields(),
        qml_properties=qml_props,
        developer_lab_properties=dev_props,
    )

    if diff["missing_in_qml"]:
        raise ValueError(f"injection contract missing_in_qml: {diff['missing_in_qml']}")
    if any(k not in dev_props for k in required_dev_props):
        raise ValueError(f"injection contract missing key developer props: {sorted(required_dev_props - dev_props)}")

    if show_diff:
        print("TASK26 injection contract diff:", diff)
        if not any(diff.values()):
            print("TASK26 injection contract diff: clean")

    print("TASK26 contracts strict ok" if strict else "TASK26 contracts ok")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--show-diff", action="store_true")
    args = parser.parse_args()
    run(strict=args.strict, show_diff=args.show_diff)


if __name__ == "__main__":
    main()
