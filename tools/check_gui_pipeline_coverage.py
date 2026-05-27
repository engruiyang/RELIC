from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui.desktop_coverage import (
    collect_cards_fields_buttons_from_pages,
    load_known_asset_ids,
    load_pipeline_bindings,
    validate_action_ids,
    validate_asset_ids,
    validate_pipeline_coverage,
    validate_safe_stop_accessible,
)
from gui.desktop_schema import (
    collect_action_ids_from_obj,
    collect_asset_ids_from_obj,
    collect_sources_from_obj,
    load_json,
    reject_script_like_values,
    validate_desktop_config,
    validate_page_config,
    validate_source_roots,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="enable strict pipeline coverage")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    examples = root / "assets" / "layouts" / "task26_examples"

    desktop_path = examples / "desktop.example.json"
    bindings_path = examples / "pipeline_ui_bindings.example.json"
    home_path = examples / "home_page.desktop_demo.json"
    training_path = examples / "training_page.desktop_demo.json"

    desktop = load_json(desktop_path)
    home = load_json(home_path)
    training = load_json(training_path)

    for p in sorted(examples.glob("*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        reject_script_like_values(obj)

    validate_desktop_config(desktop)
    validate_page_config(home)
    validate_page_config(training)

    sources = set()
    for obj in [desktop, home, training]:
        sources |= collect_sources_from_obj(obj)
    validate_source_roots(sources)

    action_ids = set()
    action_ids |= collect_action_ids_from_obj(desktop)
    action_ids |= collect_action_ids_from_obj(home)
    action_ids |= collect_action_ids_from_obj(training)
    validate_action_ids(action_ids)

    asset_ids = set()
    for obj in [desktop, home, training]:
        asset_ids |= collect_asset_ids_from_obj(obj)
    known_asset_ids = load_known_asset_ids(root / "assets" / "manifest.json", root / "assets" / "packs" / "default" / "pack.json")
    validate_asset_ids(asset_ids, known_asset_ids)

    inventory = collect_cards_fields_buttons_from_pages([home, training], desktop)
    bindings = load_pipeline_bindings(bindings_path)
    validate_pipeline_coverage(bindings, inventory, strict=args.strict)
    validate_safe_stop_accessible(inventory)

    if args.strict:
        print("TASK26 pipeline coverage strict ok")
    else:
        print("TASK26 pipeline coverage ok")


if __name__ == "__main__":
    main()
