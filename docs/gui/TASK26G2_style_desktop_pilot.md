# TASK26G-2 Style-Capable Desktop Layout + Page Pilot

## Goal

TASK26G-2 extends the real desktop layout preview so card customization changes are visible in QML, then reuses the same preview renderer in the Home and Training pages as a frontend pilot.

This task intentionally keeps the backend pipeline unchanged. It does not execute source bindings, it does not call actions, and it does not connect the real GameCanvas.

## Supported card style fields

Card style dictionaries may now carry:

- `background_color`
- `background_opacity`
- `border_color`
- `border_width`
- `corner_radius`
- `shape_type`
- `background_image`
- `glass_enabled`
- `glass_tint`
- `glass_opacity`
- `glass_highlight`

The layout payload exposes these as `cardN_*` keys so QML can render them without reading JSON files.

## Visual model

`DesktopLayoutPreview.qml` receives a prebuilt layout payload from `renderResourcesObj`.

`DesktopLayoutCardPreview.qml` renders each positioned card using `DesignCard.qml`.

`DesignCard.qml` supports a lightweight glass effect using translucent tint and highlight layers. This is a QML-native approximation intended for the current desktop-card pilot. It does not implement platform blur or shader-based glass.

## Page pilot

HomePage and TrainingPage now include a TASK26 desktop pilot section near the top of the page.

The old page content is kept as legacy fallback and can be controlled through:

- `task26DesktopPilotEnabled`
- `task26LegacyFallbackVisible`

## Boundaries

This task does not:

- modify guiBridge
- modify command_registry
- execute action_id
- execute source bindings
- read JSON files from QML
- use Loader / Repeater / Timer / subprocess
- attach the real GameCanvas
- remove legacy page content
