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

TRAINING_SLOT_INJECTION_FIELDS: tuple[str, ...] = (
    "slot_count",
    *(
        f"slot{i}_{suffix}"
        for i in range(1, 8)
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
            "placeholder",
            "role",
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
                    "args": w.get("args", {}),
                    "options": w.get("options", []),
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
                "shape": card.get("shape", ""),
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


def _widget_labels(widgets: list[dict[str, Any]], *, limit: int = 3) -> list[str]:
    labels: list[str] = []
    for w in widgets[:limit]:
        if not isinstance(w, dict):
            continue
        label = w.get("label")
        if isinstance(label, str) and label:
            labels.append(label)
        elif isinstance(w.get("id"), str) and w.get("id"):
            labels.append(w["id"])
        else:
            labels.append(str(w.get("type", "unknown")))
    return labels


def _card_placeholder_role(card_id: str, card_type: str, widgets: list[dict[str, Any]]) -> tuple[bool, str]:
    has_game_placeholder = any(
        isinstance(w, dict)
        and (w.get("type") == "game_placeholder" or w.get("id") == "game_canvas_placeholder")
        for w in widgets
    )
    if card_id == "game_canvas_card" or has_game_placeholder:
        return True, "game_canvas_placeholder"
    return False, card_type


def build_card_slots(model: dict, *, max_slots: int) -> list[dict]:
    if not isinstance(max_slots, int) or max_slots <= 0:
        raise ValueError("max_slots must be positive integer")
    cards = model.get("cards")
    if not isinstance(cards, list):
        raise ValueError("render model cards must be list")

    out: list[dict[str, Any]] = []
    for i, c in enumerate(cards[:max_slots], start=1):
        if not isinstance(c, dict):
            continue
        card_id = str(c.get("id", ""))
        card_type = str(c.get("type", ""))
        widgets = c.get("widgets") or []
        if not isinstance(widgets, list):
            widgets = []
        typed_widgets = [w for w in widgets if isinstance(w, dict)]
        action_ids = sorted({w.get("action_id") for w in typed_widgets if isinstance(w.get("action_id"), str) and w.get("action_id")})
        source_roots = sorted({str(w.get("source")).split(".", 1)[0] for w in typed_widgets if isinstance(w.get("source"), str) and w.get("source")})
        placeholder, role = _card_placeholder_role(card_id, card_type, typed_widgets)
        out.append(
            {
                "slot_index": i,
                "card_id": card_id,
                "card_type": card_type,
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
                "first_widget_labels": _widget_labels(typed_widgets),
                "placeholder": placeholder,
                "role": role,
            }
        )
    return out


def build_home_card_slots(model: dict, *, max_slots: int = 4) -> list[dict]:
    slots = build_card_slots(model, max_slots=max_slots)
    for slot in slots:
        slot.pop("placeholder", None)
        slot.pop("role", None)
    return slots

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


def _training_game_canvas_card_status(cards: list[dict[str, Any]]) -> str:
    for card in cards:
        if card.get("id") != "game_canvas_card":
            continue
        widgets = card.get("widgets") if isinstance(card.get("widgets"), list) else []
        has_placeholder = any(
            isinstance(w, dict)
            and (w.get("type") == "game_placeholder" or w.get("id") == "game_canvas_placeholder")
            for w in widgets
        )
        if card.get("type") == "game" or has_placeholder:
            return "placeholder_present"
        return "card_present_without_placeholder"
    return "missing"


def build_training_contract_summary(example_root: Path) -> dict:
    model = build_training_render_model(example_root)
    cards = model.get("cards")
    if not isinstance(cards, list):
        raise ValueError("training render model cards must be list")

    action_ids: set[str] = set()
    source_roots: set[str] = set()
    placeholder_sources: set[str] = set()
    widget_count = 0
    required_card_ids: list[str] = []

    for card in cards:
        if not isinstance(card, dict):
            continue
        if bool(card.get("required", False)):
            required_card_ids.append(str(card.get("id", "")))
        widgets = card.get("widgets") if isinstance(card.get("widgets"), list) else []
        widget_count += len(widgets)
        for widget in widgets:
            if not isinstance(widget, dict):
                continue
            action_id = widget.get("action_id")
            if isinstance(action_id, str) and action_id:
                action_ids.add(action_id)
            source = widget.get("source")
            if isinstance(source, str) and source:
                source_roots.add(source.split(".", 1)[0])
                if source in {"gameHudJson.status", "gameHudJson.score", "gameHudJson.focus_index"} or source.startswith("gameViewJson"):
                    placeholder_sources.add(source)

    action_ids_sorted = sorted(action_ids)
    return {
        "page_id": model.get("page_id", ""),
        "card_count": len(cards),
        "widget_count": widget_count,
        "required_card_ids": required_card_ids,
        "action_ids": action_ids_sorted,
        "source_roots": sorted(source_roots),
        "placeholder_sources": sorted(placeholder_sources),
        "game_canvas_card_status": _training_game_canvas_card_status(cards),
        "safe_stop_present": "live.safe_stop" in action_ids,
        "training_slots_supported": True,
        "training_injection_supported": True,
    }


def build_training_render_resource(example_root: Path) -> dict:
    return {
        "task26_training_summary": build_training_contract_summary(example_root),
        "task26_training_status": "ok",
        "task26_training_source": "assets/layouts/task26_examples/training_page.desktop_demo.json",
    }


def build_training_card_slots(example_root: Path, *, max_slots: int = 7) -> list[dict]:
    return build_card_slots(build_training_render_model(example_root), max_slots=max_slots)


def build_training_card_slots_injection_payload(slots: list[dict]) -> dict:
    if not isinstance(slots, list):
        raise ValueError("slots must be list")

    payload: dict[str, Any] = {"slot_count": min(len(slots), 7)}
    string_suffixes = {
        "card_id",
        "card_type",
        "title",
        "subtitle",
        "rect_text",
        "action_ids_text",
        "source_roots_text",
        "first_widget_labels_text",
        "role",
    }

    for idx in range(1, 8):
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
        payload[f"slot{idx}_placeholder"] = bool(slot.get("placeholder", False)) if slot else False
        payload[f"slot{idx}_role"] = str(slot.get("role", "")) if slot else ""

    # Keeps local linters from marking the set unused while documenting field classes.
    _ = string_suffixes
    return payload


def expected_training_slot_injection_fields() -> set[str]:
    return set(TRAINING_SLOT_INJECTION_FIELDS)


def validate_training_slot_injection_payload(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise ValueError("payload must be dict")

    required_fields = expected_training_slot_injection_fields()
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
        "role",
    }
    bool_suffixes = {"required", "locked", "placeholder"}

    for i in range(1, 8):
        for suffix in string_suffixes:
            key = f"slot{i}_{suffix}"
            if not isinstance(payload.get(key), str):
                raise ValueError(f"{key} must be string")
        for suffix in bool_suffixes:
            key = f"slot{i}_{suffix}"
            if not isinstance(payload.get(key), bool):
                raise ValueError(f"{key} must be bool")
        key = f"slot{i}_widget_count"
        if not isinstance(payload.get(key), int):
            raise ValueError(f"{key} must be int")


def build_training_slots_render_resource(example_root: Path) -> dict:
    payload = build_training_card_slots_injection_payload(build_training_card_slots(example_root, max_slots=7))
    validate_training_slot_injection_payload(payload)
    return {
        "task26_training_slots_payload": payload,
        "task26_training_slots_status": "ok",
        "task26_training_slots_source": "assets/layouts/task26_examples/training_page.desktop_demo.json",
    }


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



LAYOUT_PREVIEW_MAX_CARDS = 7


def _join_text_list(values: Any) -> str:
    if isinstance(values, list):
        items = [str(v) for v in values if str(v)]
        return ", ".join(items) if items else "n/a"
    return "n/a"


def _style_text(style: dict[str, Any], keys: tuple[str, ...], fallback: str) -> str:
    for key in keys:
        value = style.get(key)
        if isinstance(value, str) and value:
            return value
    return fallback


def _style_number(style: dict[str, Any], keys: tuple[str, ...], fallback: float) -> float:
    for key in keys:
        value = style.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass
    return float(fallback)


def _style_bool(style: dict[str, Any], keys: tuple[str, ...], fallback: bool) -> bool:
    for key in keys:
        value = style.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "1", "on"}:
                return True
            if lowered in {"false", "no", "0", "off"}:
                return False
    return bool(fallback)


def _card_visual_style(card: dict[str, Any]) -> dict[str, Any]:
    style = card.get("style") if isinstance(card.get("style"), dict) else {}
    return {
        "background_color": _style_text(style, ("background_color", "background", "color"), "#151B24"),
        "background_opacity": _style_number(style, ("background_opacity", "opacity"), 0.92),
        "border_color": _style_text(style, ("border_color", "border"), "#2B3A4C"),
        "border_width": int(_style_number(style, ("border_width",), 1)),
        "radius_value": int(_style_number(style, ("radius_value", "corner_radius", "radius"), 14)),
        "shape_type": _style_text(style, ("shape_type", "shape"), str(card.get("shape") or "rounded_rect")),
        "background_image": _style_text(style, ("background_image", "image"), ""),
        "glass_enabled": _style_bool(style, ("glass_enabled", "glass"), False),
        "glass_tint_color": _style_text(style, ("glass_tint_color", "glass_tint"), "#DDEEFF"),
        "glass_opacity": _style_number(style, ("glass_opacity",), 0.0),
        "glass_highlight": _style_bool(style, ("glass_highlight",), False),
        "title_pixel_size": int(_style_number(style, ("title_pixel_size", "title_size"), 15)),
        "subtitle_pixel_size": int(_style_number(style, ("subtitle_pixel_size", "subtitle_size"), 10)),
        "widget_label_pixel_size": int(_style_number(style, ("widget_label_pixel_size", "label_pixel_size", "label_size"), 10)),
        "widget_value_pixel_size": int(_style_number(style, ("widget_value_pixel_size", "value_pixel_size", "value_size"), 12)),
        "widget_meta_pixel_size": int(_style_number(style, ("widget_meta_pixel_size", "meta_pixel_size", "meta_size"), 9)),
        "widget_row_height": int(_style_number(style, ("widget_row_height", "row_height"), 22)),
        "button_height": int(_style_number(style, ("button_height",), 28)),
        "widget_spacing": int(_style_number(style, ("widget_spacing",), 3)),
        "body_top_margin": int(_style_number(style, ("body_top_margin",), 2)),
        "feedback_height": int(_style_number(style, ("feedback_height",), 34)),
        "feedback_pixel_size": int(_style_number(style, ("feedback_pixel_size",), 9)),
        "header_spacing": int(_style_number(style, ("header_spacing",), 2)),
        "content_spacing": int(_style_number(style, ("content_spacing",), 4)),
    }



def _widget_preview_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (bool, int, float)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _widget_options_text(value: Any) -> str:
    if isinstance(value, list):
        return "|".join(str(v) for v in value if str(v))
    if isinstance(value, str):
        return value
    return ""


def _add_widget_preview_fields(payload: dict[str, Any], card_prefix: str, widgets: list[dict[str, Any]], *, max_widgets: int = 6) -> None:
    typed_widgets = [w for w in widgets if isinstance(w, dict)]
    payload[f"{card_prefix}_widget_count"] = len(typed_widgets)
    for widget_idx in range(1, max_widgets + 1):
        widget = typed_widgets[widget_idx - 1] if widget_idx - 1 < len(typed_widgets) else {}
        prefix = f"{card_prefix}_widget{widget_idx}"
        payload[f"{prefix}_type"] = _widget_preview_text(widget.get("type", "")) if widget else ""
        payload[f"{prefix}_id"] = _widget_preview_text(widget.get("id", "")) if widget else ""
        payload[f"{prefix}_label"] = _widget_preview_text(widget.get("label", "")) if widget else ""
        payload[f"{prefix}_source"] = _widget_preview_text(widget.get("source", "")) if widget else ""
        payload[f"{prefix}_fallback"] = _widget_preview_text(widget.get("fallback", "")) if widget else ""
        payload[f"{prefix}_unit"] = _widget_preview_text(widget.get("unit", "")) if widget else ""
        payload[f"{prefix}_action_id"] = _widget_preview_text(widget.get("action_id", "")) if widget else ""
        payload[f"{prefix}_args_json"] = _widget_preview_text(widget.get("args", {})) if widget else "{}"
        payload[f"{prefix}_options_text"] = _widget_options_text(widget.get("options", [])) if widget else ""
        payload[f"{prefix}_variant"] = _widget_preview_text(widget.get("variant", "")) if widget else ""
        payload[f"{prefix}_required"] = bool(widget.get("required", False)) if widget else False
        payload[f"{prefix}_value"] = _widget_preview_text(widget.get("value", "")) if widget else ""

def build_desktop_layout_preview_payload(model: dict, *, max_cards: int = LAYOUT_PREVIEW_MAX_CARDS) -> dict:
    if not isinstance(max_cards, int) or max_cards <= 0:
        raise ValueError("max_cards must be positive integer")

    layout = model.get("layout")
    if not isinstance(layout, dict):
        raise ValueError("render model layout must be object")

    cards = model.get("cards")
    if not isinstance(cards, list):
        raise ValueError("render model cards must be list")

    payload: dict[str, Any] = {
        "page_id": str(model.get("page_id", "")),
        "page_width": float(layout.get("page_width", 1200) or 1200),
        "page_height": float(layout.get("page_height", 800) or 800),
        "card_count": min(len(cards), max_cards),
        "max_cards": max_cards,
    }

    for idx in range(1, max_cards + 1):
        card = cards[idx - 1] if idx - 1 < len(cards) and isinstance(cards[idx - 1], dict) else {}
        widgets = card.get("widgets") if isinstance(card.get("widgets"), list) else []
        typed_widgets = [w for w in widgets if isinstance(w, dict)]
        action_ids = sorted({w.get("action_id") for w in typed_widgets if isinstance(w.get("action_id"), str) and w.get("action_id")})
        source_roots = sorted({str(w.get("source")).split(".", 1)[0] for w in typed_widgets if isinstance(w.get("source"), str) and w.get("source")})
        first_widget_labels = _widget_labels(typed_widgets)
        card_id = str(card.get("id", "")) if card else ""
        card_type = str(card.get("type", "")) if card else ""
        placeholder, role = _card_placeholder_role(card_id, card_type, typed_widgets) if card else (False, "")

        payload[f"card{idx}_visible"] = bool(card)
        payload[f"card{idx}_id"] = card_id
        payload[f"card{idx}_type"] = card_type
        payload[f"card{idx}_title"] = str(card.get("title", "")) if card else ""
        payload[f"card{idx}_subtitle"] = str(card.get("subtitle", "")) if card else ""
        payload[f"card{idx}_x"] = float(card.get("x", 0) or 0) if card else 0.0
        payload[f"card{idx}_y"] = float(card.get("y", 0) or 0) if card else 0.0
        payload[f"card{idx}_width"] = float(card.get("width", 0) or 0) if card else 0.0
        payload[f"card{idx}_height"] = float(card.get("height", 0) or 0) if card else 0.0
        payload[f"card{idx}_required"] = bool(card.get("required", False)) if card else False
        payload[f"card{idx}_locked"] = bool(card.get("locked", False)) if card else False
        _add_widget_preview_fields(payload, f"card{idx}", typed_widgets)
        payload[f"card{idx}_action_ids_text"] = _join_text_list(action_ids)
        payload[f"card{idx}_source_roots_text"] = _join_text_list(source_roots)
        payload[f"card{idx}_first_widget_labels_text"] = _join_text_list(first_widget_labels)
        payload[f"card{idx}_placeholder"] = bool(placeholder)
        payload[f"card{idx}_role"] = str(role)

        visual_style = _card_visual_style(card) if card else _card_visual_style({})
        payload[f"card{idx}_background_color"] = visual_style["background_color"]
        payload[f"card{idx}_background_opacity"] = visual_style["background_opacity"]
        payload[f"card{idx}_border_color"] = visual_style["border_color"]
        payload[f"card{idx}_border_width"] = visual_style["border_width"]
        payload[f"card{idx}_radius_value"] = visual_style["radius_value"]
        payload[f"card{idx}_shape_type"] = visual_style["shape_type"]
        payload[f"card{idx}_background_image"] = visual_style["background_image"]
        payload[f"card{idx}_glass_enabled"] = visual_style["glass_enabled"]
        payload[f"card{idx}_glass_tint_color"] = visual_style["glass_tint_color"]
        payload[f"card{idx}_glass_opacity"] = visual_style["glass_opacity"]
        payload[f"card{idx}_glass_highlight"] = visual_style["glass_highlight"]
        payload[f"card{idx}_title_pixel_size"] = visual_style["title_pixel_size"]
        payload[f"card{idx}_subtitle_pixel_size"] = visual_style["subtitle_pixel_size"]
        payload[f"card{idx}_widget_label_pixel_size"] = visual_style["widget_label_pixel_size"]
        payload[f"card{idx}_widget_value_pixel_size"] = visual_style["widget_value_pixel_size"]
        payload[f"card{idx}_widget_meta_pixel_size"] = visual_style["widget_meta_pixel_size"]
        payload[f"card{idx}_widget_row_height"] = visual_style["widget_row_height"]
        payload[f"card{idx}_button_height"] = visual_style["button_height"]
        payload[f"card{idx}_widget_spacing"] = visual_style["widget_spacing"]
        payload[f"card{idx}_body_top_margin"] = visual_style["body_top_margin"]
        payload[f"card{idx}_feedback_height"] = visual_style["feedback_height"]
        payload[f"card{idx}_feedback_pixel_size"] = visual_style["feedback_pixel_size"]
        payload[f"card{idx}_header_spacing"] = visual_style["header_spacing"]
        payload[f"card{idx}_content_spacing"] = visual_style["content_spacing"]

    return payload


def validate_desktop_layout_preview_payload(payload: dict, *, max_cards: int = LAYOUT_PREVIEW_MAX_CARDS) -> None:
    if not isinstance(payload, dict):
        raise ValueError("layout preview payload must be dict")
    for key in ("page_id",):
        if not isinstance(payload.get(key), str):
            raise ValueError(f"{key} must be string")
    for key in ("page_width", "page_height"):
        if not isinstance(payload.get(key), (int, float)) or float(payload.get(key)) <= 0:
            raise ValueError(f"{key} must be positive number")
    for key in ("card_count", "max_cards"):
        if not isinstance(payload.get(key), int):
            raise ValueError(f"{key} must be int")

    for idx in range(1, max_cards + 1):
        for suffix in ("visible", "required", "locked", "placeholder"):
            key = f"card{idx}_{suffix}"
            if not isinstance(payload.get(key), bool):
                raise ValueError(f"{key} must be bool")
        for suffix in ("id", "type", "title", "subtitle", "action_ids_text", "source_roots_text", "first_widget_labels_text", "role", "background_color", "border_color", "shape_type", "background_image", "glass_tint_color"):
            key = f"card{idx}_{suffix}"
            if not isinstance(payload.get(key), str):
                raise ValueError(f"{key} must be string")
        for suffix in ("x", "y", "width", "height", "background_opacity", "border_width", "radius_value", "glass_opacity", "title_pixel_size", "subtitle_pixel_size", "widget_label_pixel_size", "widget_value_pixel_size", "widget_meta_pixel_size", "widget_row_height", "button_height", "widget_spacing", "body_top_margin", "feedback_height", "feedback_pixel_size", "header_spacing", "content_spacing"):
            key = f"card{idx}_{suffix}"
            if not isinstance(payload.get(key), (int, float)):
                raise ValueError(f"{key} must be number")
        key = f"card{idx}_widget_count"
        if not isinstance(payload.get(key), int):
            raise ValueError(f"{key} must be int")
        for widget_idx in range(1, 7):
            for suffix in ("type", "id", "label", "source", "fallback", "unit", "action_id", "args_json", "options_text", "variant", "value"):
                widget_key = f"card{idx}_widget{widget_idx}_{suffix}"
                if not isinstance(payload.get(widget_key), str):
                    raise ValueError(f"{widget_key} must be string")
            widget_required_key = f"card{idx}_widget{widget_idx}_required"
            if not isinstance(payload.get(widget_required_key), bool):
                raise ValueError(f"{widget_required_key} must be bool")
        for suffix in ("glass_enabled", "glass_highlight"):
            key = f"card{idx}_{suffix}"
            if not isinstance(payload.get(key), bool):
                raise ValueError(f"{key} must be bool")


def build_home_layout_preview_payload(example_root: Path) -> dict:
    payload = build_desktop_layout_preview_payload(build_home_render_model(example_root), max_cards=4)
    validate_desktop_layout_preview_payload(payload, max_cards=4)
    return payload


def build_training_layout_preview_payload(example_root: Path) -> dict:
    payload = build_desktop_layout_preview_payload(build_training_render_model(example_root), max_cards=7)
    validate_desktop_layout_preview_payload(payload, max_cards=7)
    return payload


def build_home_layout_render_resource(example_root: Path) -> dict:
    return {
        "task26_home_layout_payload": build_home_layout_preview_payload(example_root),
        "task26_home_layout_status": "ok",
        "task26_home_layout_source": "assets/layouts/task26_examples/home_page.desktop_demo.json",
    }


def build_training_layout_render_resource(example_root: Path) -> dict:
    return {
        "task26_training_layout_payload": build_training_layout_preview_payload(example_root),
        "task26_training_layout_status": "ok",
        "task26_training_layout_source": "assets/layouts/task26_examples/training_page.desktop_demo.json",
    }



TASK26_PAGE_DEMO_FILENAMES: dict[str, str] = {
    "home": "home_page.desktop_demo.json",
    "training": "training_page.desktop_demo.json",
    "user": "user_page.desktop_demo.json",
    "calibration": "calibration_page.desktop_demo.json",
    "report": "report_page.desktop_demo.json",
    "diagnostics": "diagnostics_page.desktop_demo.json",
}

TASK26_PAGE_LAYOUT_RESOURCE_KEYS: dict[str, str] = {
    "home": "task26_home_layout",
    "training": "task26_training_layout",
    "user": "task26_user_layout",
    "calibration": "task26_calibration_layout",
    "report": "task26_report_layout",
    "diagnostics": "task26_diagnostics_layout",
}


def task26_page_demo_path(example_root: Path, page_id: str) -> Path:
    page_id = str(page_id or "").strip()
    filename = TASK26_PAGE_DEMO_FILENAMES.get(page_id)
    if not filename:
        raise ValueError(f"unsupported TASK26 page_id: {page_id}")
    return example_root / "assets" / "layouts" / "task26_examples" / filename


def build_task26_page_render_model(example_root: Path, page_id: str) -> dict:
    page_path = task26_page_demo_path(example_root, page_id)
    with page_path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise ValueError(f"{page_path.name} must be object")
    return build_page_render_model(config)


def build_task26_page_layout_preview_payload(example_root: Path, page_id: str, *, max_cards: int = 7) -> dict:
    payload = build_desktop_layout_preview_payload(
        build_task26_page_render_model(example_root, page_id),
        max_cards=max_cards,
    )
    validate_desktop_layout_preview_payload(payload, max_cards=max_cards)
    return payload


def build_task26_page_layout_render_resource(example_root: Path, page_id: str, *, max_cards: int = 7) -> dict:
    resource_key = TASK26_PAGE_LAYOUT_RESOURCE_KEYS.get(page_id)
    if not resource_key:
        raise ValueError(f"unsupported TASK26 layout resource page_id: {page_id}")
    return {
        f"{resource_key}_payload": build_task26_page_layout_preview_payload(example_root, page_id, max_cards=max_cards),
        f"{resource_key}_status": "ok",
        f"{resource_key}_source": f"assets/layouts/task26_examples/{TASK26_PAGE_DEMO_FILENAMES[page_id]}",
    }


def build_user_layout_render_resource(example_root: Path) -> dict:
    return build_task26_page_layout_render_resource(example_root, "user", max_cards=7)


def build_calibration_layout_render_resource(example_root: Path) -> dict:
    return build_task26_page_layout_render_resource(example_root, "calibration", max_cards=7)


def build_report_layout_render_resource(example_root: Path) -> dict:
    return build_task26_page_layout_render_resource(example_root, "report", max_cards=7)


def build_diagnostics_layout_render_resource(example_root: Path) -> dict:
    return build_task26_page_layout_render_resource(example_root, "diagnostics", max_cards=7)


FIXED_CARD_REQUIRED_POLICY_KEYS: tuple[str, ...] = (
    "allow_move",
    "allow_resize",
    "allow_remove",
    "allow_collapse",
)


def _as_policy(card: dict[str, Any], *, page_id: str) -> dict[str, Any]:
    card_id = str(card.get("id") or "")
    policy = card.get("card_policy")
    if not isinstance(policy, dict):
        raise ValueError(f"{page_id}:{card_id}: card_policy must be object")
    for key in FIXED_CARD_REQUIRED_POLICY_KEYS:
        if key not in policy:
            raise ValueError(f"{page_id}:{card_id}: card_policy missing {key}")
        if not isinstance(policy.get(key), bool):
            raise ValueError(f"{page_id}:{card_id}: card_policy.{key} must be bool")
    return policy


def _card_action_ids(card: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    widgets = card.get("widgets") if isinstance(card.get("widgets"), list) else []
    for widget in widgets:
        if not isinstance(widget, dict):
            continue
        action_id = widget.get("action_id")
        if isinstance(action_id, str) and action_id:
            out.add(action_id)
    return out


def _card_has_required_widget(card: dict[str, Any]) -> bool:
    widgets = card.get("widgets") if isinstance(card.get("widgets"), list) else []
    return any(isinstance(widget, dict) and bool(widget.get("required", False)) for widget in widgets)


def _fixed_card_reasons(card: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if bool(card.get("required", False)):
        reasons.append("required_card")
    if bool(card.get("locked", False)):
        reasons.append("locked_card")
    if _card_has_required_widget(card):
        reasons.append("required_widget")
    action_ids = _card_action_ids(card)
    if "live.safe_stop" in action_ids:
        reasons.append("safe_stop_action")
    return sorted(set(reasons))


def is_task26_fixed_card(card: dict[str, Any]) -> bool:
    return bool(_fixed_card_reasons(card))


def validate_task26_page_fixed_card_policy(page_config: dict[str, Any]) -> None:
    page_id = str(page_config.get("page_id") or "unknown")
    cards = page_config.get("cards")
    if not isinstance(cards, list) or not cards:
        raise ValueError(f"{page_id}: cards must be non-empty list")

    seen: set[str] = set()
    fixed_count = 0
    for card in cards:
        if not isinstance(card, dict):
            raise ValueError(f"{page_id}: card must be object")
        card_id = str(card.get("id") or "")
        if not card_id:
            raise ValueError(f"{page_id}: card id is required")
        if card_id in seen:
            raise ValueError(f"{page_id}:{card_id}: duplicate card id")
        seen.add(card_id)

        policy = _as_policy(card, page_id=page_id)
        reasons = _fixed_card_reasons(card)
        fixed = bool(reasons)
        if fixed:
            fixed_count += 1
            if card.get("required") is not True:
                raise ValueError(f"{page_id}:{card_id}: fixed card must have required=true")
            if card.get("locked") is not True:
                raise ValueError(f"{page_id}:{card_id}: fixed card must have locked=true")
            if policy.get("allow_remove") is not False:
                raise ValueError(f"{page_id}:{card_id}: fixed card cannot allow_remove")
        else:
            if card.get("required") is True or card.get("locked") is True:
                raise ValueError(f"{page_id}:{card_id}: optional card cannot be required/locked")
            if policy.get("allow_remove") is not True:
                raise ValueError(f"{page_id}:{card_id}: optional card must allow_remove")

    if fixed_count <= 0:
        raise ValueError(f"{page_id}: at least one fixed card is required")


def build_task26_fixed_card_registry_from_configs(page_configs: list[dict[str, Any]]) -> dict[str, Any]:
    pages: dict[str, Any] = {}
    total_fixed = 0
    total_optional = 0
    forbidden_removal: list[str] = []

    for page in page_configs:
        page_id = str(page.get("page_id") or "unknown")
        validate_task26_page_fixed_card_policy(page)
        page_cards: list[dict[str, Any]] = []
        fixed_card_ids: list[str] = []
        optional_card_ids: list[str] = []
        cards = page.get("cards") if isinstance(page.get("cards"), list) else []
        for card in cards:
            if not isinstance(card, dict):
                continue
            card_id = str(card.get("id") or "")
            policy = _as_policy(card, page_id=page_id)
            action_ids = sorted(_card_action_ids(card))
            reasons = _fixed_card_reasons(card)
            fixed = bool(reasons)
            if fixed:
                fixed_card_ids.append(card_id)
                forbidden_removal.append(f"{page_id}:{card_id}")
                total_fixed += 1
            else:
                optional_card_ids.append(card_id)
                total_optional += 1
            page_cards.append(
                {
                    "card_id": card_id,
                    "fixed": fixed,
                    "reasons": reasons,
                    "required": bool(card.get("required", False)),
                    "locked": bool(card.get("locked", False)),
                    "allow_move": bool(policy.get("allow_move", False)),
                    "allow_resize": bool(policy.get("allow_resize", False)),
                    "allow_remove": bool(policy.get("allow_remove", False)),
                    "allow_collapse": bool(policy.get("allow_collapse", False)),
                    "action_ids": action_ids,
                }
            )
        pages[page_id] = {
            "fixed_card_ids": fixed_card_ids,
            "optional_card_ids": optional_card_ids,
            "fixed_count": len(fixed_card_ids),
            "optional_count": len(optional_card_ids),
            "cards": page_cards,
        }

    return {
        "version": "task26.fixed_cards.v1",
        "pages": pages,
        "fixed_card_count": total_fixed,
        "optional_card_count": total_optional,
        "forbidden_removal_card_refs": sorted(forbidden_removal),
    }


def _load_task26_page_config(example_root: Path, page_id: str) -> dict[str, Any]:
    page_path = task26_page_demo_path(example_root, page_id)
    with page_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{page_path.name} must be object")
    return data


def build_task26_fixed_card_registry(example_root: Path, *, page_ids: list[str] | None = None) -> dict[str, Any]:
    page_ids = page_ids or list(TASK26_PAGE_DEMO_FILENAMES.keys())
    page_configs = [_load_task26_page_config(example_root, page_id) for page_id in page_ids]
    return build_task26_fixed_card_registry_from_configs(page_configs)


def validate_task26_fixed_card_policy(example_root: Path, *, page_ids: list[str] | None = None) -> None:
    build_task26_fixed_card_registry(example_root, page_ids=page_ids)


def _grid_rect_for_card(card: dict[str, Any], *, page_id: str) -> tuple[str, int, int, int, int]:
    card_id = str(card.get("id") or "")
    pos = card.get("position")
    if not isinstance(pos, dict):
        raise ValueError(f"{page_id}:{card_id}: position must be object")

    col = _as_pos_int(pos.get("col"), field="col", card_id=card_id)
    row = _as_pos_int(pos.get("row"), field="row", card_id=card_id)
    col_span = _as_pos_int(pos.get("col_span"), field="col_span", card_id=card_id)
    row_span = _as_pos_int(pos.get("row_span"), field="row_span", card_id=card_id)
    return (card_id, col, row, col + col_span - 1, row + row_span - 1)


def _grid_rects_overlap(a: tuple[str, int, int, int, int], b: tuple[str, int, int, int, int]) -> bool:
    return not (
        a[3] < b[1]
        or b[3] < a[1]
        or a[4] < b[2]
        or b[4] < a[2]
    )


def validate_task26_page_layout_no_overlap(page_config: dict[str, Any]) -> None:
    if not isinstance(page_config, dict):
        raise ValueError("page_config must be object")

    page_id = str(page_config.get("page_id") or "unknown")
    cards = page_config.get("cards")
    if not isinstance(cards, list):
        raise ValueError(f"{page_id}: cards must be list")

    rects: list[tuple[str, int, int, int, int]] = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        rects.append(_grid_rect_for_card(card, page_id=page_id))

    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            if _grid_rects_overlap(a, b):
                raise ValueError(
                    f"{page_id}: desktop cards overlap: "
                    f"{a[0]}({a[1]},{a[2]}-{a[3]},{a[4]}) "
                    f"overlaps {b[0]}({b[1]},{b[2]}-{b[3]},{b[4]})"
                )


def validate_task26_layout_no_overlap(example_root: Path, *, page_ids: list[str] | None = None) -> None:
    page_ids = page_ids or list(TASK26_PAGE_DEMO_FILENAMES.keys())
    for page_id in page_ids:
        validate_task26_page_layout_no_overlap(_load_task26_page_config(example_root, page_id))


def build_task26_fixed_card_render_resource(example_root: Path) -> dict[str, Any]:
    return {
        "task26_fixed_card_registry": build_task26_fixed_card_registry(example_root),
        "task26_fixed_card_status": "ok",
        "task26_fixed_card_source": "assets/layouts/task26_examples/*.desktop_demo.json",
    }


def write_render_model(model: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
