from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_BANNED = ["function", "eval", "script", "javascript:", "=>", "onclicked", "qt.calllater"]
_SOURCE_BANNED = ["..", "/", "\\n", "(", ")", ";", "=", "=>", "javascript:", "eval", "function", "onclicked", "qt.calllater"]

ALLOWED_SOURCE_ROOTS: set[str] = {
    "appState",
    "runtimeSnapshot",
    "sessionState",
    "controlState",
    "controlStateJson",
    "gameHud",
    "gameHudJson",
    "gameView",
    "gameViewJson",
    "renderResources",
    "renderResourcesJson",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return data


def iter_task26_example_json(root: Path) -> list[Path]:
    return sorted((root / "assets" / "layouts" / "task26_examples").glob("*.json"))


def reject_script_like_values(obj: object, path: str = "$") -> None:
    def _check_text(text: str, where: str) -> None:
        low = text.lower()
        for token in _BANNED:
            if token in low:
                raise ValueError(f"script-like token '{token}' at {where}")

    if isinstance(obj, dict):
        for k, v in obj.items():
            _check_text(str(k), f"{path}.<key>")
            reject_script_like_values(v, f"{path}.{k}")
        return
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            reject_script_like_values(v, f"{path}[{i}]")
        return
    if isinstance(obj, str):
        _check_text(obj, path)


validate_no_script_like_json = reject_script_like_values


def validate_desktop_config(config: dict[str, Any]) -> None:
    if not config.get("desktop_id"):
        raise ValueError("desktop_id is required")
    status_bar = config.get("status_bar")
    if not isinstance(status_bar, dict) or status_bar.get("locked") is not True:
        raise ValueError("status_bar.locked must be true")
    dock = config.get("dock")
    if not isinstance(dock, dict) or dock.get("locked") is not True:
        raise ValueError("dock.locked must be true")
    pages = config.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("pages must be non-empty list")
    buttons = dock.get("buttons") or []
    found_safe_stop = False
    for item in buttons:
        if isinstance(item, str) and item == "live.safe_stop":
            found_safe_stop = True
            break
        if isinstance(item, dict) and item.get("action_id") == "live.safe_stop":
            found_safe_stop = True
            break
    if not found_safe_stop:
        raise ValueError("dock.buttons must contain live.safe_stop")
    if "wallpaper" not in config:
        raise ValueError("wallpaper is required")


def validate_page_config(config: dict[str, Any]) -> None:
    if not config.get("page_id"):
        raise ValueError("page_id is required")
    if not isinstance(config.get("layout"), dict):
        raise ValueError("layout is required")
    cards = config.get("cards")
    if not isinstance(cards, list):
        raise ValueError("cards must be a list")

    for idx, card in enumerate(cards):
        if not isinstance(card, dict):
            raise ValueError(f"card[{idx}] must be object")
        for key in ["id", "type", "position", "widgets"]:
            if key not in card:
                raise ValueError(f"card[{idx}] missing {key}")
        if card.get("required") is True and card.get("locked") is not True:
            raise ValueError(f"card[{idx}] required=true must have locked=true")
        pos = card.get("position")
        if not isinstance(pos, dict):
            raise ValueError(f"card[{idx}].position must be object")
        for g in ["col", "row", "col_span", "row_span"]:
            if g not in pos:
                raise ValueError(f"card[{idx}].position missing {g}")
        widgets = card.get("widgets")
        if not isinstance(widgets, list):
            raise ValueError(f"card[{idx}].widgets must be list")
        for widx, w in enumerate(widgets):
            if not isinstance(w, dict):
                raise ValueError(f"card[{idx}].widgets[{widx}] must be object")
            if w.get("type") == "button" and "action_id" in w and not isinstance(w.get("action_id"), str):
                raise ValueError(f"card[{idx}].widgets[{widx}].action_id must be string")
            for conditional_key in ["enabled_when", "visible_when"]:
                if conditional_key in w and not isinstance(w[conditional_key], (str, dict)):
                    raise ValueError(f"card[{idx}].widgets[{widx}].{conditional_key} must be str|dict")


def collect_action_ids_from_obj(obj: object) -> set[str]:
    out: set[str] = set()

    def _walk(node: object, parent_key: str | None = None) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "action_id" and isinstance(v, str):
                    out.add(v)
                _walk(v, k)
        elif isinstance(node, list):
            for item in node:
                if parent_key == "buttons" and isinstance(item, str):
                    out.add(item)
                _walk(item, parent_key)

    _walk(obj)
    return out


def collect_asset_ids_from_obj(obj: object) -> set[str]:
    out: set[str] = set()

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("asset_id"), str):
                out.add(node["asset_id"])
            bg = node.get("background_image")
            if isinstance(bg, dict) and isinstance(bg.get("asset_id"), str):
                out.add(bg["asset_id"])
            wp = node.get("wallpaper")
            if isinstance(wp, dict) and isinstance(wp.get("asset_id"), str):
                out.add(wp["asset_id"])
            if node.get("type") == "image" and isinstance(node.get("asset_id"), str):
                out.add(node["asset_id"])
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(obj)
    return out


def collect_sources_from_obj(obj: object) -> set[str]:
    sources: set[str] = set()

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            src = node.get("source")
            if isinstance(src, str):
                sources.add(src)
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(obj)
    return sources


def validate_source_roots(sources: set[str]) -> None:
    if not sources:
        return
    for src in sources:
        if not isinstance(src, str):
            raise ValueError(f"source must be string: {src!r}")
        low = src.lower()
        for token in _SOURCE_BANNED:
            if token in low:
                raise ValueError(f"invalid source token in '{src}'")
        root = src.split(".", 1)[0]
        if root not in ALLOWED_SOURCE_ROOTS:
            raise ValueError(f"invalid source root in '{src}'")
