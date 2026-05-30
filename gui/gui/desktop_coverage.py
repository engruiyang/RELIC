from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gui.command_registry import build_page_command_manifest

NATIVE_ACTION_IDS: set[str] = {
    "live.safe_stop",
    "nav.home",
    "nav.training",
    "nav.calibration",
    "nav.report",
    "nav.diagnostics",
    "nav.developer",
}


def get_command_registry_action_ids() -> set[str]:
    manifest = build_page_command_manifest()
    pages = manifest.get("pages") or {}
    action_ids: set[str] = set()
    for commands in pages.values():
        for cmd in commands:
            native = cmd.get("native_action_id")
            if isinstance(native, str) and native:
                action_ids.add(native)
    return action_ids


def validate_action_ids(action_ids: set[str]) -> None:
    allowed = get_command_registry_action_ids() | NATIVE_ACTION_IDS
    unknown = sorted(a for a in action_ids if a not in allowed)
    if unknown:
        raise ValueError(f"unknown action_id(s): {', '.join(unknown)}")


def load_pipeline_bindings(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict) and isinstance(raw.get("pipelines"), list):
        items = raw["pipelines"]
    else:
        raise ValueError("pipeline bindings must be list or {pipelines:[...]}")
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"pipeline[{i}] must be object")
    return items


def collect_cards_fields_buttons_from_pages(page_configs: list[dict[str, Any]], desktop_config: dict[str, Any]) -> dict[str, set[str]]:
    cards: set[str] = set()
    fields: set[str] = set()
    buttons: set[str] = set()

    dock = desktop_config.get("dock") or {}
    for b in dock.get("buttons") or []:
        if isinstance(b, str):
            buttons.add(b)
        elif isinstance(b, dict) and isinstance(b.get("action_id"), str):
            buttons.add(b["action_id"])

    for page in page_configs:
        for card in page.get("cards") or []:
            cid = card.get("id")
            if isinstance(cid, str) and cid:
                cards.add(cid)
            for w in card.get("widgets") or []:
                src = w.get("source")
                if isinstance(src, str) and src:
                    fields.add(src)
                aid = w.get("action_id")
                if isinstance(aid, str) and aid:
                    buttons.add(aid)

    return {"cards": cards, "fields": fields, "buttons": buttons}


def validate_pipeline_coverage(bindings: list[dict[str, Any]], inventory: dict[str, set[str]], strict: bool = False) -> None:
    errors: list[str] = []
    for item in bindings:
        if item.get("mandatory") is not True:
            continue
        pid = str(item.get("pipeline_id") or "unknown")

        req_cards = [str(x) for x in (item.get("required_cards") or []) if isinstance(x, str)]
        req_fields = [str(x) for x in (item.get("required_fields") or []) if isinstance(x, str)]
        req_buttons = [str(x) for x in (item.get("required_buttons") or []) if isinstance(x, str)]
        allowed_pages = item.get("allowed_pages")

        if not isinstance(allowed_pages, list) or not allowed_pages:
            errors.append(f"{pid}: allowed_pages must be non-empty")
        if not item.get("fallback_card"):
            errors.append(f"{pid}: fallback_card missing")
        if not isinstance(item.get("coverage_policy"), dict):
            errors.append(f"{pid}: coverage_policy missing")

        if strict:
            miss_cards = [c for c in req_cards if c not in inventory["cards"]]
            miss_fields = [f for f in req_fields if f not in inventory["fields"]]
            miss_buttons = [b for b in req_buttons if b not in inventory["buttons"]]
            if miss_cards:
                errors.append(f"{pid}: strict missing required_cards {miss_cards}")
            if miss_fields:
                errors.append(f"{pid}: strict missing required_fields {miss_fields}")
            if miss_buttons:
                errors.append(f"{pid}: strict missing required_buttons {miss_buttons}")
        else:
            if req_cards and not any(c in inventory["cards"] for c in req_cards):
                errors.append(f"{pid}: missing required_cards any-of {req_cards}")
            if req_fields and not any(f in inventory["fields"] for f in req_fields):
                errors.append(f"{pid}: missing required_fields any-of {req_fields}")
            if req_buttons and not any(b in inventory["buttons"] for b in req_buttons):
                errors.append(f"{pid}: missing required_buttons any-of {req_buttons}")

    if errors:
        raise ValueError("pipeline coverage failed: " + " | ".join(errors))


def validate_safe_stop_accessible(inventory: dict[str, set[str]]) -> None:
    if "live.safe_stop" not in inventory.get("buttons", set()):
        raise ValueError("live.safe_stop is not accessible")


def load_known_asset_ids(manifest_path: Path, pack_path: Path) -> set[str]:
    known: set[str] = set()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pack = json.loads(pack_path.read_text(encoding="utf-8"))

    common = manifest.get("common_assets") or {}
    if isinstance(common, dict):
        known.update(str(k) for k in common.keys())
        for desc in common.values():
            if isinstance(desc, dict):
                url = desc.get("url")
                if isinstance(url, str) and url:
                    known.add(Path(url).stem)

    def _scan(node: object) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                lk = str(k).lower()
                if "asset" in lk or "slot" in lk:
                    known.add(str(k))
                    if isinstance(v, str):
                        known.add(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str):
                                known.add(item)
                    elif isinstance(v, dict):
                        known.update(str(x) for x in v.keys())
                _scan(v)
        elif isinstance(node, list):
            for item in node:
                _scan(item)

    _scan(manifest)
    _scan(pack)
    return {x for x in known if x}


def validate_asset_ids(asset_ids: set[str], known_asset_ids: set[str]) -> None:
    if not asset_ids:
        return
    unknown: list[str] = []
    for aid in sorted(asset_ids):
        if aid.startswith("preview_") or aid.startswith("placeholder_"):
            continue
        if aid not in known_asset_ids:
            unknown.append(aid)
    if unknown:
        raise ValueError(f"unknown asset_id(s): {', '.join(unknown)}")
