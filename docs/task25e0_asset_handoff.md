# TASK25E-0 Asset Handoff Contract

TASK25E-0 defines the artist-facing replacement contract for RELIC design packs.

This stage intentionally does **not** include real images, fonts, or audio. Artists can later place licensed assets in the directories below and update `assets/manifest.json` URL fields. QML and control logic should not be edited during normal art replacement.

## Directory layout

```text
assets/packs/default/images/backgrounds/
assets/packs/default/images/ui/
assets/packs/default/images/trace_lock/
assets/packs/default/images/effects/
assets/packs/default/audio/ui/
assets/packs/default/audio/trace_lock/
assets/packs/default/fonts/
```

## Replacement rules

1. Keep `url: null` until real art is ready.
2. Use relative URLs under `packs/default/`.
3. Do not edit TraceLock scoring, difficulty, session, report, calibration, or user logic for art replacement.
4. Do not commit unlicensed images, fonts, or audio.
5. Prefer system fonts unless redistribution permission is clear.
6. Missing art must fall back to color, gradient, shape, particle, or silent fallback.

## Slot groups

The authoritative list is in:

```text
assets/packs/default/asset_handoff.json
assets/manifest.json
```

Important groups include page backgrounds, UI button/frame slots, TraceLock target/canvas slots, TraceLock effect slots, optional audio slots, and optional font slots.
