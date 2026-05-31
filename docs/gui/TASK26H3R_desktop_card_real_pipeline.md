# TASK26H-3R Desktop Card Real Control/Data Pipeline Reconnect

This patch reconnects desktop card widgets to the real GUI bridge and runtime state objects.

## Key points

- Button widgets remain card widgets from desktop JSON.
- No standalone old panel flow is introduced.
- DesktopLayoutCardPreview now logs `[DESKTOP CARD CLICK]` before invoking the bridge.
- It logs `[DESKTOP CARD ACTION]` after the bridge returns.
- It displays last action feedback inside the card.
- Pages pass explicit `guiBridge`, runtime, session, control, HUD and render resource objects to DesktopLayoutPreview.
- MinimalGui passes these objects to all page components.
- GuiBridge emits stateChanged after invokeAction so MinimalGui pulls fresh state.
- GuiFacade supports report command aliases used by desktop JSON.
- Card text rows are compact and clipped with elision to avoid overflow.

## Still deferred

- Real GameCanvas rendering.
- Drag/resize editor.
- Full action args editor UI.
