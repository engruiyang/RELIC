from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui.desktop_model import build_home_render_model, build_page_render_model, write_render_model
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
    args = parser.parse_args()

    if args.page != "home":
        raise SystemExit("only home is supported in TASK26E-0")

    example_root = ROOT
    if args.width == 1200 and args.height == 800:
        model = build_home_render_model(example_root)
    else:
        page_cfg = load_json(example_root / "assets/layouts/task26_examples/home_page.desktop_demo.json")
        model = build_page_render_model(page_cfg, page_width=args.width, page_height=args.height)

    out_path = ROOT / args.output
    write_render_model(model, out_path)
    print(f"TASK26 render model written: {args.output}")


if __name__ == "__main__":
    main()
