from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _as_pos_int(value: Any, *, field: str, card_id: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"card {card_id}: {field} must be positive integer")
    return value


def build_page_render_model(page_config: dict, *, page_width: int = 1200, page_height: int = 800) -> dict:
    layout = page_config.get("layout")
    if not isinstance(layout, dict):
        raise ValueError("layout must be object")
    if layout.get("mode") != "grid":
        raise ValueError("only grid layout is supported")

    columns = int(layout.get("columns", 0))
    rows = int(layout.get("rows", 0))
    gap = float(layout.get("gap", 0))
    padding = float(layout.get("padding", 0))

    if columns <= 0 or rows <= 0:
        raise ValueError("layout.columns and layout.rows must be positive")

    usable_width = page_width - padding * 2
    usable_height = page_height - padding * 2
    cell_width = (usable_width - gap * (columns - 1)) / columns
    cell_height = (usable_height - gap * (rows - 1)) / rows

    cards_in = page_config.get("cards")
    if not isinstance(cards_in, list):
        raise ValueError("cards must be list")

    cards_out: list[dict[str, Any]] = []
    for card in cards_in:
        if not isinstance(card, dict):
            raise ValueError("card must be object")
        card_id = card.get("id")
        if not isinstance(card_id, str) or not card_id:
            raise ValueError("card id is required")

        pos = card.get("position")
        if not isinstance(pos, dict):
            raise ValueError(f"card {card_id}: position is required")

        col = _as_pos_int(pos.get("col"), field="col", card_id=card_id)
        row = _as_pos_int(pos.get("row"), field="row", card_id=card_id)
        col_span = _as_pos_int(pos.get("col_span"), field="col_span", card_id=card_id)
        row_span = _as_pos_int(pos.get("row_span"), field="row_span", card_id=card_id)

        if col + col_span - 1 > columns or row + row_span - 1 > rows:
            raise ValueError(f"card {card_id}: out of grid boundary")

        x = padding + (col - 1) * (cell_width + gap)
        y = padding + (row - 1) * (cell_height + gap)
        width = cell_width * col_span + gap * (col_span - 1)
        height = cell_height * row_span + gap * (row_span - 1)

        widgets_in = card.get("widgets")
        if not isinstance(widgets_in, list):
            raise ValueError(f"card {card_id}: widgets must be list")

        widgets_out: list[dict[str, Any]] = []
        for i, w in enumerate(widgets_in):
            if not isinstance(w, dict):
                raise ValueError(f"card {card_id}: widget[{i}] must be object")
            w_type = w.get("type")
            if not isinstance(w_type, str) or not w_type:
                raise ValueError(f"card {card_id}: widget[{i}] type is required")
            wid = w.get("id") if isinstance(w.get("id"), str) else f"{card_id}_widget_{i}"
            action_id = w.get("action_id")
            if action_id is not None and not isinstance(action_id, str):
                raise ValueError(f"card {card_id}: widget {wid} action_id must be string")
            widgets_out.append(
                {
                    "id": wid,
                    "type": w_type,
                    "label": w.get("label", ""),
                    "value": w.get("value"),
                    "source": w.get("source", ""),
                    "fallback": w.get("fallback", ""),
                    "unit": w.get("unit", ""),
                    "action_id": action_id,
                    "variant": w.get("variant", ""),
                    "required": bool(w.get("required", False)),
                    "style": w.get("style", {}),
                    "enabled_when": w.get("enabled_when"),
                    "visible_when": w.get("visible_when"),
                }
            )

        cards_out.append(
            {
                "id": card_id,
                "type": card.get("type", ""),
                "title": card.get("title", ""),
                "subtitle": card.get("subtitle", ""),
                "required": bool(card.get("required", False)),
                "locked": bool(card.get("locked", False)),
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "preset": card.get("preset", ""),
                "style": card.get("style", {}),
                "widgets": widgets_out,
            }
        )

    return {
        "page_id": page_config.get("page_id", ""),
        "title": page_config.get("title", ""),
        "subtitle": page_config.get("subtitle", ""),
        "layout": {
            "mode": "grid",
            "columns": columns,
            "rows": rows,
            "gap": gap,
            "padding": padding,
            "page_width": page_width,
            "page_height": page_height,
            "cell_width": cell_width,
            "cell_height": cell_height,
        },
        "cards": cards_out,
    }


def build_render_model_summary(model: dict) -> dict:
    cards = model.get("cards")
    if not isinstance(cards, list):
        raise ValueError("render model cards must be list")

    card_ids = [str(c.get("id", "")) for c in cards]
    card_count = len(cards)
    required_card_count = sum(1 for c in cards if bool(c.get("required", False)))
    locked_card_count = sum(1 for c in cards if bool(c.get("locked", False)))

    widget_count = 0
    action_ids: set[str] = set()
    source_roots: set[str] = set()

    for c in cards:
        widgets = c.get("widgets") or []
        if not isinstance(widgets, list):
            continue
        widget_count += len(widgets)
        for w in widgets:
            if not isinstance(w, dict):
                continue
            aid = w.get("action_id")
            if isinstance(aid, str) and aid:
                action_ids.add(aid)
            src = w.get("source")
            if isinstance(src, str) and src:
                source_roots.add(src.split(".", 1)[0])

    action_ids_sorted = sorted(action_ids)
    source_roots_sorted = sorted(source_roots)
    preview_lines = [
        f"Page: {model.get('page_id', 'n/a')}",
        f"Cards: {card_count}",
        f"Widgets: {widget_count}",
        f"Required cards: {required_card_count}",
        f"Locked cards: {locked_card_count}",
        f"Actions: {', '.join(action_ids_sorted) if action_ids_sorted else 'n/a'}",
    ]

    return {
        "page_id": model.get("page_id", ""),
        "card_count": card_count,
        "widget_count": widget_count,
        "required_card_count": required_card_count,
        "locked_card_count": locked_card_count,
        "action_ids": action_ids_sorted,
        "source_roots": source_roots_sorted,
        "card_ids": card_ids,
        "preview_lines": preview_lines,
    }


def build_home_render_model(example_root: Path) -> dict:
    page_path = example_root / "assets" / "layouts" / "task26_examples" / "home_page.desktop_demo.json"
    with page_path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise ValueError("home_page.desktop_demo.json must be object")
    return build_page_render_model(config)


def build_home_render_model_summary(example_root: Path) -> dict:
    return build_render_model_summary(build_home_render_model(example_root))


def write_render_model(model: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
