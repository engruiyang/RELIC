# TASK26G-3 Multi-page Desktop Pilot

This patch extends the TASK26 desktop card pilot from Home/Training to the remaining primary pages:

- User
- Calibration
- Report
- Diagnostics

The goal is full-area, phone-desktop style card coverage. The pilot overlay fills the page content area with only a small margin. It does not consume the global shell sidebar or top navigation area.

## Design policy

The RELIC desktop GUI keeps two card classes:

1. Mandatory I/O and safety cards
   - required=true
   - locked=true
   - may be moved, resized, recolored, re-skinned, and collapsed only when policy allows
   - must remain covered by contract checks

2. Optional cards
   - may be added, removed, moved, resized, recolored, and re-skinned
   - must not be the only path to safety or required pipeline state

## Implementation

Each new page receives a JSON desktop demo file under:

```text
assets/layouts/task26_examples
```

Each page receives a render resource:

```text
task26_user_layout_payload
task26_calibration_layout_payload
task26_report_layout_payload
task26_diagnostics_layout_payload
```

Each page overlays the existing legacy page with `DesktopLayoutPreview`. The legacy QML remains in the file and can be restored by setting `task26DesktopPilotEnabled` to false.

## Screen usage

The pilot overlay uses:

```qml
anchors.fill: parent
anchors.margins: 6
```

This leaves only a narrow visual gap inside the page body and avoids wasting useful content area.

## Boundaries

This patch does not:

- change guiBridge
- change command execution
- change runtime/session/game logic
- connect a real GameCanvas
- add drag editing
- add runtime layout persistence
- remove legacy pages
