from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HOME_SLOT_INJECTION_FIELDS: tuple[str, ...] = (
    "slot_count",
    *(
        f"slot{i}_{suffix}"
        for i in range(1, 5)
        for suffix in (
            "card_id",
            "card_type",
            "title",
            "subtitle",
            "required",
            "locked",
            "rect_text",
            "widget_count",
            "action_ids_text",
            "source_roots_text",
            "first_widget_labels_text",
        )
    ),
)


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


def build_home_card_slots(model: dict, *, max_slots: int = 4) -> list[dict]:
    if not isinstance(max_slots, int) or max_slots <= 0:
        raise ValueError("max_slots must be positive integer")
    cards = model.get("cards")
    if not isinstance(cards, list):
        raise ValueError("render model cards must be list")

    out: list[dict[str, Any]] = []
    for i, c in enumerate(cards[:max_slots], start=1):
        card_id = str(c.get("id", ""))
        widgets = c.get("widgets") or []
        if not isinstance(widgets, list):
            widgets = []
        action_ids = sorted({w.get("action_id") for w in widgets if isinstance(w, dict) and isinstance(w.get("action_id"), str) and w.get("action_id")})
        source_roots = sorted({str(w.get("source")).split(".", 1)[0] for w in widgets if isinstance(w, dict) and isinstance(w.get("source"), str) and w.get("source")})
        labels: list[str] = []
        for w in widgets[:3]:
            if not isinstance(w, dict):
                continue
            label = w.get("label")
            if isinstance(label, str) and label:
                labels.append(label)
            elif isinstance(w.get("id"), str) and w.get("id"):
                labels.append(w["id"])
            else:
                labels.append(str(w.get("type", "unknown")))
        out.append(
            {
                "slot_index": i,
                "card_id": card_id,
                "card_type": c.get("type", ""),
                "title": c.get("title", ""),
                "subtitle": c.get("subtitle", ""),
                "required": bool(c.get("required", False)),
                "locked": bool(c.get("locked", False)),
                "x": c.get("x", 0),
                "y": c.get("y", 0),
                "width": c.get("width", 0),
                "height": c.get("height", 0),
                "widget_count": len(widgets),
                "action_ids": action_ids,
                "source_roots": source_roots,
                "first_widget_labels": labels,
            }
        )
    return out


def build_home_render_model(example_root: Path) -> dict:
    page_path = example_root / "assets" / "layouts" / "task26_examples" / "home_page.desktop_demo.json"
    with page_path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise ValueError("home_page.desktop_demo.json must be object")
    return build_page_render_model(config)


def build_home_render_model_summary(example_root: Path) -> dict:
    return build_render_model_summary(build_home_render_model(example_root))


def build_training_render_model(example_root: Path) -> dict:
    page_path = example_root / "assets" / "layouts" / "task26_examples" / "training_page.desktop_demo.json"
    with page_path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise ValueError("training_page.desktop_demo.json must be object")
    return build_page_render_model(config)


def build_training_render_model_summary(example_root: Path) -> dict:
    return build_render_model_summary(build_training_render_model(example_root))


def build_home_card_slots_from_examples(example_root: Path, *, max_slots: int = 4) -> list[dict]:
    return build_home_card_slots(build_home_render_model(example_root), max_slots=max_slots)


def build_home_card_slots_injection_payload(slots: list[dict]) -> dict:
    if not isinstance(slots, list):
        raise ValueError("slots must be list")

    payload: dict[str, Any] = {"slot_count": min(len(slots), 4)}

    for idx in range(1, 5):
        slot = slots[idx - 1] if idx - 1 < len(slots) and isinstance(slots[idx - 1], dict) else {}
        action_ids = slot.get("action_ids") if isinstance(slot.get("action_ids"), list) else []
        source_roots = slot.get("source_roots") if isinstance(slot.get("source_roots"), list) else []
        first_widget_labels = slot.get("first_widget_labels") if isinstance(slot.get("first_widget_labels"), list) else []

        payload[f"slot{idx}_card_id"] = str(slot.get("card_id", "")) if slot else ""
        payload[f"slot{idx}_card_type"] = str(slot.get("card_type", "")) if slot else ""
        payload[f"slot{idx}_title"] = str(slot.get("title", "")) if slot else ""
        payload[f"slot{idx}_subtitle"] = str(slot.get("subtitle", "")) if slot else ""
        payload[f"slot{idx}_required"] = bool(slot.get("required", False)) if slot else False
        payload[f"slot{idx}_locked"] = bool(slot.get("locked", False)) if slot else False

        x = slot.get("x", 0) if slot else 0
        y = slot.get("y", 0) if slot else 0
        width = slot.get("width", 0) if slot else 0
        height = slot.get("height", 0) if slot else 0
        payload[f"slot{idx}_rect_text"] = f"x={x}, y={y}, w={width}, h={height}"
        payload[f"slot{idx}_widget_count"] = int(slot.get("widget_count", 0)) if slot else 0
        payload[f"slot{idx}_action_ids_text"] = ", ".join(str(x) for x in action_ids) if action_ids else "n/a"
        payload[f"slot{idx}_source_roots_text"] = ", ".join(str(x) for x in source_roots) if source_roots else "n/a"
        payload[f"slot{idx}_first_widget_labels_text"] = ", ".join(str(x) for x in first_widget_labels) if first_widget_labels else "n/a"

    return payload


def build_home_card_slots_injection_payload_from_examples(example_root: Path) -> dict:
    slots = build_home_card_slots_from_examples(example_root, max_slots=4)
    return build_home_card_slots_injection_payload(slots)


def build_home_slots_render_resource(example_root: Path) -> dict:
    payload = build_home_card_slots_injection_payload_from_examples(example_root)
    validate_home_slot_injection_payload(payload)
    return {
        "task26_home_slots_payload": payload,
        "task26_home_slots_status": "ok",
        "task26_home_slots_source": "assets/layouts/task26_examples/home_page.desktop_demo.json",
    }


def expected_home_slot_injection_fields() -> set[str]:
    return set(HOME_SLOT_INJECTION_FIELDS)


def snake_to_qml_camel(name: str) -> str:
    parts = name.split("_")
    if not parts:
        return name
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


def expected_home_slot_qml_properties() -> set[str]:
    return {snake_to_qml_camel(field) for field in expected_home_slot_injection_fields()}


def diff_home_slot_injection_contract(
    payload_fields: set[str],
    qml_properties: set[str],
    developer_lab_properties: set[str],
) -> dict:
    payload_camel = {snake_to_qml_camel(name) for name in payload_fields}

    missing_in_qml = sorted(payload_camel - qml_properties)
    missing_in_developer_lab = sorted(payload_camel - developer_lab_properties)
    extra_in_qml = sorted(qml_properties - payload_camel)
    extra_in_developer_lab = sorted(developer_lab_properties - payload_camel)

    return {
        "missing_in_qml": missing_in_qml,
        "missing_in_developer_lab": missing_in_developer_lab,
        "extra_in_qml": extra_in_qml,
        "extra_in_developer_lab": extra_in_developer_lab,
    }


def validate_home_slot_injection_payload(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise ValueError("payload must be dict")

    required_fields = expected_home_slot_injection_fields()
    missing = sorted(required_fields - set(payload.keys()))
    if missing:
        raise ValueError(f"missing injection field: {missing[0]}")

    if not isinstance(payload.get("slot_count"), int):
        raise ValueError("slot_count must be int")

    string_suffixes = {
        "card_id",
        "card_type",
        "title",
        "subtitle",
        "rect_text",
        "action_ids_text",
        "source_roots_text",
        "first_widget_labels_text",
    }

    for i in range(1, 5):
        for suffix in string_suffixes:
            key = f"slot{i}_{suffix}"
            if not isinstance(payload.get(key), str):
                raise ValueError(f"{key} must be string")

        for suffix in ("required", "locked"):
            key = f"slot{i}_{suffix}"
            if not isinstance(payload.get(key), bool):
                raise ValueError(f"{key} must be bool")

        key = f"slot{i}_widget_count"
        if not isinstance(payload.get(key), int):
            raise ValueError(f"{key} must be int")

    # Unknown extra fields are intentionally allowed in TASK26E-3B.


def write_render_model(model: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
