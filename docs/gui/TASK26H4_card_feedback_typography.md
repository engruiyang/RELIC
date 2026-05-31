# TASK26H-4 Card Feedback, Typography, and Missing Actions

This patch tightens the desktop-card GUI after the real button bridge started working.

## Goals

- Keep every operation inside the desktop-card widget pipeline.
- Replace raw JSON feedback in cards with short action summaries.
- Keep full raw action JSON in console logs for debugging.
- Make card typography and row spacing configurable from each card's `style` object.
- Add missing desktop action buttons for user creation and calibration start/show/bind.

## New style fields

Each card may define:

```json
{
  "title_pixel_size": 15,
  "subtitle_pixel_size": 10,
  "widget_label_pixel_size": 10,
  "widget_value_pixel_size": 12,
  "widget_meta_pixel_size": 9,
  "widget_row_height": 20,
  "button_height": 24,
  "widget_spacing": 3,
  "body_top_margin": 1,
  "feedback_height": 34,
  "feedback_pixel_size": 9,
  "header_spacing": 1,
  "content_spacing": 3
}
```

These fields are compiled by `gui/desktop_model.py` into `cardN_*` layout payload fields, passed by `DesktopLayoutPreview.qml`, and consumed by `DesktopLayoutCardPreview.qml` and `DesignCard.qml`.

## Feedback behavior

`DesktopLayoutCardPreview.qml` still logs full raw action results to the console, but the in-card feedback line now uses compact summaries such as:

- `accepted · 7 users`
- `accepted · 4 calibrations`
- `completed · mock session completed`
- `noop · no_active_session`
- `unsupported · live_control_required`

## Boundaries

- No new action execution path.
- No GameCanvas integration in this patch.
- No backend session/calibration/report logic rewrite.
- All added controls remain JSON-declared card widgets.
