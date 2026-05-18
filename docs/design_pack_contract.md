# TASK25A Design Pack Contract

This document defines the JSON-only contract for `assets/packs/default`.

- No GUI logic changes are required.
- No QML page rewrites are required.
- No binary art payloads are required in TASK25A.

`pack.json` defines pointers to theme, page/component/game/effect style descriptors.
`core.resource_managers.build_render_resource_bundle(...)` now exports both legacy render fields and design-pack fields with safe fallback behavior.
