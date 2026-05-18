from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class GameVisualManifest:
    schema_version: str
    game_id: str
    assets: dict[str, dict[str, Any]]
    effects: dict[str, dict[str, Any]]
    styles: dict[str, str]
    supported_entities: list[str]


@dataclass(slots=True)
class RenderResourceBundle:
    theme_id: str
    layout_id: str
    game_id: str
    assets: dict[str, dict[str, Any]] = field(default_factory=dict)
    styles: dict[str, dict[str, Any]] = field(default_factory=dict)
    layout_regions: dict[str, dict[str, Any]] = field(default_factory=dict)
    missing_assets: list[str] = field(default_factory=list)
    missing_styles: list[str] = field(default_factory=list)
    missing_regions: list[str] = field(default_factory=list)
    design_pack: dict[str, Any] = field(default_factory=dict)
    theme: dict[str, Any] = field(default_factory=dict)
    page_styles: dict[str, dict[str, Any]] = field(default_factory=dict)
    component_styles: dict[str, dict[str, Any]] = field(default_factory=dict)
    game_styles: dict[str, dict[str, Any]] = field(default_factory=dict)
    effect_styles: dict[str, dict[str, Any]] = field(default_factory=dict)
    asset_handoff: dict[str, Any] = field(default_factory=dict)
    asset_handoff_validation: dict[str, Any] = field(default_factory=dict)
    missing_design_pack_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AssetManager:
    def __init__(self, assets_root: str = "assets") -> None:
        self.assets_root = Path(assets_root)
        self.manifest = self._read_json(self.assets_root / "manifest.json")

    @property
    def asset_count(self) -> int:
        total = len((self.manifest.get("common_assets") or {}).keys())
        for gid in (self.manifest.get("games") or {}).keys():
            total += len(self._load_visual_manifest(gid).assets)
        return total

    def _read_json(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _load_visual_manifest(self, game_id: str) -> GameVisualManifest:
        games = self.manifest.get("games") or {}
        game_def = games.get(game_id) or {}
        rel = game_def.get("visual_manifest") or f"games/{game_id}/visual_manifest.json"
        raw = self._read_json(self.assets_root / rel)
        return GameVisualManifest(
            schema_version=str(raw.get("schema_version") or ""),
            game_id=str(raw.get("game_id") or game_id),
            assets=dict(raw.get("assets") or {}),
            effects=dict(raw.get("effects") or {}),
            styles=dict(raw.get("styles") or {}),
            supported_entities=list(raw.get("supported_entities") or []),
        )

    def load_game_visual_manifest(self, game_id: str) -> GameVisualManifest:
        return self._load_visual_manifest(game_id)

    def resolve_asset(self, game_id: str, asset_key: str, *, fallback_key: str = "common.placeholder.circle") -> dict[str, Any]:
        vm = self._load_visual_manifest(game_id)
        desc = vm.assets.get(asset_key)
        source = f"games/{game_id}/visual_manifest"
        exists = True
        if desc is None:
            exists = False
            desc = (self.manifest.get("common_assets") or {}).get(fallback_key) or {}
            source = "common_assets" if desc else "missing"
        return {
            "asset_key": asset_key,
            "type": desc.get("type"),
            "url": desc.get("url"),
            "fallback_shape": desc.get("fallback_shape"),
            "style_key": desc.get("style_key"),
            "source": source,
            "exists": exists,
            "description": desc.get("description", ""),
        }


class ThemeManager:
    def __init__(self, assets_root: str = "assets", theme_id: str = "default") -> None:
        self.assets_root = Path(assets_root)
        self.theme = self._read_json(self.assets_root / "themes" / theme_id / "theme.json")
        self.theme_id = str(self.theme.get("theme_id") or theme_id)

    def _read_json(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def style_count(self) -> int:
        return len((self.theme.get("styles") or {}).keys())

    def resolve_style(self, style_key: str, *, fallback_key: str = "panel.debug") -> dict[str, Any]:
        styles = self.theme.get("styles") or {}
        style = styles.get(style_key)
        exists = True
        source = "theme.styles"
        if style is None:
            exists = False
            style = styles.get(fallback_key) or {}
            source = "theme.styles.fallback" if style else "missing"
        return {
            "style_key": style_key,
            "fill": style.get("fill"),
            "stroke": style.get("stroke"),
            "stroke_width": style.get("stroke_width"),
            "opacity": style.get("opacity"),
            "font_size": style.get("font_size"),
            "debug_label": style.get("debug_label"),
            "source": source,
            "exists": exists,
        }


class LayoutManager:
    def __init__(self, assets_root: str = "assets", layout_id: str = "minimal_gui") -> None:
        self.assets_root = Path(assets_root)
        self.layout = self._read_json(self.assets_root / "layouts" / f"{layout_id}.json")
        self.layout_id = str(self.layout.get("layout_id") or layout_id)

    def _read_json(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def resolve_region(self, region_key: str) -> dict[str, Any]:
        regions = self.layout.get("regions") or {}
        region = regions.get(region_key)
        exists = True
        source = "layout.regions"
        if region is None:
            exists = False
            region = regions.get("root") or {}
            source = "layout.regions.fallback" if region else "missing"
        return {
            "region_key": region_key,
            "x": region.get("x"),
            "y": region.get("y"),
            "width": region.get("width"),
            "height": region.get("height"),
            "anchor": region.get("anchor"),
            "visible": region.get("visible"),
            "source": source,
            "exists": exists,
        }



def _safe_read_json_file(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return raw if isinstance(raw, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def validate_design_pack_asset_handoff(assets_root: str = "assets", pack_id: str = "default") -> dict[str, Any]:
    """Validate TASK25E-0 artist handoff slots without requiring real binary assets.

    A null URL is valid at this stage because renderers must use color/shape fallbacks.
    Non-null URLs must stay inside the pack's relative asset directories and use allowed extensions.
    """
    root = Path(assets_root)
    manifest = _safe_read_json_file(root / "manifest.json")
    pack_root = root / "packs" / pack_id
    pack = _safe_read_json_file(pack_root / "pack.json")
    handoff_rel = str(pack.get("asset_handoff") or "asset_handoff.json")
    handoff = _safe_read_json_file(pack_root / handoff_rel)

    common_assets = dict(manifest.get("common_assets") or {})
    slot_groups = dict(pack.get("asset_slot_groups") or {})
    expected_slots: list[str] = []
    for group_slots in slot_groups.values():
        expected_slots.extend([str(s) for s in group_slots])

    missing_slots = sorted([slot for slot in expected_slots if slot not in common_assets])

    allowed_extensions_raw = handoff.get("allowed_extensions") or {}
    allowed_extensions: set[str] = set()
    for value in allowed_extensions_raw.values():
        if isinstance(value, list):
            allowed_extensions.update(str(v).lower() for v in value)

    directories = dict(handoff.get("directories") or pack.get("asset_directories") or {})
    allowed_prefixes = ["packs/default/"]
    allowed_prefixes.extend(str(v) for v in directories.values())

    invalid_url_assets: list[str] = []
    real_asset_urls: list[str] = []
    null_url_assets: list[str] = []

    for key, desc in common_assets.items():
        url = desc.get("url")
        if url in (None, ""):
            null_url_assets.append(str(key))
            continue
        url_s = str(url)
        real_asset_urls.append(url_s)
        suffix = Path(url_s).suffix.lower()
        prefix_ok = any(url_s.startswith(prefix) for prefix in allowed_prefixes)
        ext_ok = suffix in allowed_extensions if allowed_extensions else True
        if not prefix_ok or not ext_ok:
            invalid_url_assets.append(str(key))

    return {
        "pack_id": pack_id,
        "slot_count": len(common_assets),
        "expected_slot_count": len(set(expected_slots)),
        "missing_slots": missing_slots,
        "invalid_url_assets": sorted(invalid_url_assets),
        "real_asset_urls": sorted(real_asset_urls),
        "null_url_asset_count": len(null_url_assets),
        "allowed_extensions": sorted(allowed_extensions),
        "directories": directories,
        "asset_handoff": handoff,
    }

def build_render_resource_bundle(game_id: str, theme_id: str = "default", layout_id: str = "minimal_gui", assets_root: str = "assets") -> dict[str, Any]:
    am = AssetManager(assets_root=assets_root)
    tm = ThemeManager(assets_root=assets_root, theme_id=theme_id)
    lm = LayoutManager(assets_root=assets_root, layout_id=layout_id)
    vm = am.load_game_visual_manifest(game_id)

    assets: dict[str, dict[str, Any]] = {}
    styles: dict[str, dict[str, Any]] = {}
    missing_assets: list[str] = []
    missing_styles: list[str] = []
    for key in vm.assets.keys():
        a = am.resolve_asset(game_id, key)
        assets[key] = a
        if not a.get("exists"):
            missing_assets.append(key)
        sk = a.get("style_key")
        if sk:
            s = tm.resolve_style(str(sk))
            styles[str(sk)] = s
            if not s.get("exists"):
                missing_styles.append(str(sk))

    # TASK25B: expose common design/background asset slots in renderResourcesJson as well.
    # These keys are safe placeholders until real images are provided in TASK25E.
    for common_key, desc in (am.manifest.get("common_assets") or {}).items():
        if common_key not in assets:
            assets[str(common_key)] = {
                "asset_key": str(common_key),
                "type": desc.get("type"),
                "url": desc.get("url"),
                "fallback_shape": desc.get("fallback_shape"),
                "style_key": desc.get("style_key"),
                "source": "common_assets",
                "exists": bool(desc),
                "description": desc.get("description", ""),
            }

    layout_regions: dict[str, dict[str, Any]] = {}
    missing_regions: list[str] = []
    for rk in ["root", "game_canvas", "status_panel", "live_panel", "debug_panel"]:
        reg = lm.resolve_region(rk)
        layout_regions[rk] = reg
        if not reg.get("exists"):
            missing_regions.append(rk)

    def _safe_read_json(path: Path) -> dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            return raw if isinstance(raw, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    pack_root = Path(assets_root) / "packs" / "default"
    pack = _safe_read_json(pack_root / "pack.json")
    required_pack_fields = ["pack_id", "display_name", "version", "theme", "pages", "components", "games", "effects", "fallback_pack"]
    missing_design_pack_fields = [f"pack.{k}" for k in required_pack_fields if k not in pack]

    theme = _safe_read_json(pack_root / str(pack.get("theme") or "theme.json"))
    asset_handoff = _safe_read_json(pack_root / str(pack.get("asset_handoff") or "asset_handoff.json"))
    asset_handoff_validation = validate_design_pack_asset_handoff(assets_root=assets_root, pack_id=str(pack.get("pack_id") or "default"))
    pages_map = dict(pack.get("pages") or {})
    components_map = dict(pack.get("components") or {})
    games_map = dict(pack.get("games") or {})
    effects_map = dict(pack.get("effects") or {})

    page_styles = {k: _safe_read_json(pack_root / str(v)) for k, v in pages_map.items()}
    component_styles = {k: _safe_read_json(pack_root / str(v)) for k, v in components_map.items()}
    game_styles = {k: _safe_read_json(pack_root / str(v)) for k, v in games_map.items()}
    effect_styles = {k: _safe_read_json(pack_root / str(v)) for k, v in effects_map.items()}

    for key, val in [("pages", page_styles), ("components", component_styles), ("games", game_styles), ("effects", effect_styles)]:
        if not val:
            missing_design_pack_fields.append(f"pack.{key}")

    bundle = RenderResourceBundle(
        theme_id=tm.theme_id,
        layout_id=lm.layout_id,
        game_id=game_id,
        assets=assets,
        styles=styles,
        layout_regions=layout_regions,
        missing_assets=missing_assets,
        missing_styles=missing_styles,
        missing_regions=missing_regions,
        design_pack=pack,
        theme=theme,
        page_styles=page_styles,
        component_styles=component_styles,
        game_styles=game_styles,
        effect_styles=effect_styles,
        asset_handoff=asset_handoff,
        asset_handoff_validation=asset_handoff_validation,
        missing_design_pack_fields=missing_design_pack_fields,
    )
    return bundle.to_dict()
