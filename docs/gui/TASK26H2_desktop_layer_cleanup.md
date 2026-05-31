# TASK26H-2 Desktop Layer Cleanup and Non-overlap Gate

This task makes the desktop card layer the only interactive layer by default while keeping the legacy page panels as a disabled fallback.

## Goals

- Desktop pilot is visible and enabled by default.
- Legacy panels are still present, but default to `visible: false` and `enabled: false`.
- Desktop card overlaps are rejected by the contract gate.
- Current Home and Training demo layouts no longer contain overlapping cards.
- Desktop button signal handlers use explicit function parameters to avoid QML deprecation warnings.

## Layer policy

Every page keeps two layers:

- Desktop layer: `visible/enabled: task26DesktopPilotEnabled`, `z: 100`, `anchors.margins: 6`.
- Legacy layer: `visible/enabled: task26LegacyFallbackVisible`.

This prevents old buttons from receiving clicks through the new desktop pilot and makes button-origin testing reliable.

## Non-overlap policy

The checker compares every card's grid rectangle:

- left = col
- right = col + col_span - 1
- top = row
- bottom = row + row_span - 1

Any intersecting pair raises `ValueError: desktop cards overlap`.

## Current layout fixes

- Home: `relic_identity_card` moved to the lower-right free area.
- Training: `game_canvas_card` moved to rows 6-8 to avoid `game_hud_card`.

## Boundary

This task does not change backend actions, command registry, training logic, GameCanvas logic, or runtime data sources.
