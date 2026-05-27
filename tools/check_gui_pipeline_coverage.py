from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui.desktop_coverage import (
    collect_cards_fields_buttons_from_pages,
    load_pipeline_bindings,
    validate_action_ids,
    validate_pipeline_coverage,
    validate_safe_stop_accessible,
)
from gui.desktop_schema import (
    collect_action_ids_from_obj,
    load_json,
    reject_script_like_values,
    validate_desktop_config,
    validate_page_config,
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    examples = root / "assets" / "layouts" / "task26_examples"

    desktop_path = examples / "desktop.example.json"
    bindings_path = examples / "pipeline_ui_bindings.example.json"
    home_path = examples / "home_page.desktop_demo.json"
    training_path = examples / "training_page.desktop_demo.json"

    desktop = load_json(desktop_path)
    home = load_json(home_path)
    training = load_json(training_path)

    import json
    for p in sorted(examples.glob("*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        reject_script_like_values(obj)

    validate_desktop_config(desktop)
    validate_page_config(home)
    validate_page_config(training)

    action_ids = set()
    action_ids |= collect_action_ids_from_obj(desktop)
    action_ids |= collect_action_ids_from_obj(home)
    action_ids |= collect_action_ids_from_obj(training)
    validate_action_ids(action_ids)

    inventory = collect_cards_fields_buttons_from_pages([home, training], desktop)
    bindings = load_pipeline_bindings(bindings_path)
    validate_pipeline_coverage(bindings, inventory)
    validate_safe_stop_accessible(inventory)

    print("TASK26 pipeline coverage ok")


if __name__ == "__main__":
    main()
