# TASK26G-4 Fixed Card Policy

This task introduces the fixed-card gate for the RELIC desktop-card GUI.

The desktop GUI now separates cards into two groups:

1. **Fixed cards**: mandatory I/O, safety, session, calibration, report, diagnostics, training, and other pipeline-critical cards. These cards may be moved, resized, recolored, re-skinned, and visually customized when their `card_policy` allows it, but they must not be removable.
2. **Optional cards**: non-critical display, notes, brand, helper, and decorative cards. These cards may be removed, reordered, moved, resized, and styled.

## Fixed card rules

A card is treated as fixed when any of these are true:

- `required` is `true`
- `locked` is `true`
- the card contains a widget with `required: true`
- the card contains `live.safe_stop`

A fixed card must satisfy:

```json
{
  "required": true,
  "locked": true,
  "card_policy": {
    "allow_remove": false
  }
}
```

`allow_move`, `allow_resize`, and `allow_collapse` are allowed to be page-specific. For example, Training can keep some cards less movable while User / Report / Diagnostics can allow more layout freedom.

## Optional card rules

A non-fixed card must satisfy:

```json
{
  "required": false,
  "locked": false,
  "card_policy": {
    "allow_remove": true
  }
}
```

This makes optional cards safe for later editor features such as add, remove, reorder, recolor, resize, and background-image replacement.

## Why this is needed

The final RELIC GUI is a phone-desktop-like card system. The user can freely customize card size, position, colors, borders, transparency, background images, and shapes. However, critical pipelines must never lose their visible panels or buttons.

The fixed-card policy creates this boundary:

- freedom for visual design
- no accidental deletion of mandatory runtime/safety/control panels
- strong compatibility with future display-pipeline replacement

## New render resource

`GuiFacade.get_render_resources()` now exposes:

```text
task26_fixed_card_registry
task26_fixed_card_status
task26_fixed_card_source
```

This is intended for future editor panels and display-pipeline replacement logic.

## Current scope

This task does not add drag-and-drop editing.
It does not change backend commands.
It does not execute actions from QML.
It does not replace the display pipeline yet.

It only makes fixed vs optional card policy machine-checkable.
