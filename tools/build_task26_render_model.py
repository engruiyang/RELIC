from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui.desktop_model import (
    build_home_card_slots_from_examples,
    build_home_card_slots_injection_payload_from_examples,
    build_home_render_model,
    build_home_render_model_summary,
    build_page_render_model,
    build_training_card_slots,
    build_training_card_slots_injection_payload,
    build_training_render_model,
    build_training_render_model_summary,
    write_render_model,
)
from gui.desktop_schema import load_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", default="home")
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=800)
    parser.add_argument(
        "--output",
        default="assets/layouts/task26_examples/home_desktop_render_model.example.json",
    )
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--slots", action="store_true")
    parser.add_argument("--injection", action="store_true")
    args = parser.parse_args()

    if args.page not in {"home", "training"}:
        raise SystemExit("only home and training are supported in TASK26 render model builds")

    example_root = ROOT
    if args.page == "home":
        if args.width == 1200 and args.height == 800:
            model = build_home_render_model(example_root)
        else:
            page_cfg = load_json(example_root / "assets/layouts/task26_examples/home_page.desktop_demo.json")
            model = build_page_render_model(page_cfg, page_width=args.width, page_height=args.height)
        output = args.output
    else:
        if args.output == "assets/layouts/task26_examples/home_desktop_render_model.example.json":
            output = "assets/layouts/task26_examples/training_desktop_render_model.example.json"
        else:
            output = args.output
        if args.width == 1200 and args.height == 800:
            model = build_training_render_model(example_root)
        else:
            page_cfg = load_json(example_root / "assets/layouts/task26_examples/training_page.desktop_demo.json")
            model = build_page_render_model(page_cfg, page_width=args.width, page_height=args.height)

    out_path = ROOT / output
    write_render_model(model, out_path)
    print(f"TASK26 render model written: {output}")

    if args.summary:
        if args.page == "home":
            summary = build_home_render_model_summary(example_root)
            summary_rel = "assets/layouts/task26_examples/home_desktop_render_model_summary.example.json"
        else:
            summary = build_training_render_model_summary(example_root)
            summary_rel = "assets/layouts/task26_examples/training_desktop_render_model_summary.example.json"
        summary_output = ROOT / summary_rel
        write_render_model(summary, summary_output)
        print(f"TASK26 render model summary written: {summary_rel}")

    if args.slots:
        if args.page == "home":
            slots = build_home_card_slots_from_examples(example_root, max_slots=4)
            slots_payload = {"page_id": "home", "max_slots": 4, "slots": slots}
            slots_rel = "assets/layouts/task26_examples/home_desktop_render_model_slots.example.json"
        else:
            slots = build_training_card_slots(example_root, max_slots=7)
            slots_payload = {"page_id": "training", "max_slots": 7, "slots": slots}
            slots_rel = "assets/layouts/task26_examples/training_desktop_render_model_slots.example.json"
        write_render_model(slots_payload, ROOT / slots_rel)
        print(f"TASK26 render model slots written: {slots_rel}")

    if args.injection:
        if args.page == "home":
            injection = build_home_card_slots_injection_payload_from_examples(example_root)
            injection_rel = "assets/layouts/task26_examples/home_desktop_render_model_slots_injection.example.json"
        else:
            training_slots = build_training_card_slots(example_root, max_slots=7)
            injection = build_training_card_slots_injection_payload(training_slots)
            injection_rel = "assets/layouts/task26_examples/training_desktop_render_model_slots_injection.example.json"
        write_render_model(injection, ROOT / injection_rel)
        print(f"TASK26 render model slots injection written: {injection_rel}")


if __name__ == "__main__":
    main()
