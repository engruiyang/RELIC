# TASK26H-1 Desktop Card Functional Pipeline Integration

This task connects the desktop card preview pipeline to card-local functional widgets. It is not a backend rewrite and it does not replace the full display pipeline.

## Scope

- `DesktopLayoutPreview` remains responsible for placing card previews from the render-resource layout payload.
- `DesktopLayoutCardPreview` renders the first six flattened widgets from each card.
- Supported card-local widget types are `text`, `metric`, `button`, `hud`, `image`, and `game_placeholder`.
- Button widgets reuse the existing QML-to-Python action path through `guiBridge.invokeAction(actionId, "{}")`, which is backed by `GuiFacade.invoke_action`.
- The layout payload is still generated from the desktop JSON/render model and does not execute widget sources or actions.

## Source resolution

`sourceValue` is a fixed whitelist mapping for known desktop JSON source strings such as `runtimeSnapshot.*`, `sessionState.*`, `controlState*`, `gameHudJson.*`, `gameViewJson.*`, selected `appState.*`, and selected `renderResourcesJson.*` entries. It does not evaluate strings, dynamically walk arbitrary paths, or read JSON files from QML.

## Existing safety boundaries

- Fixed card policy remains enforced by the existing registry and deletion policy.
- Legacy fallback sections remain available on the migrated pages.
- `game_placeholder` only displays a GameCanvas placeholder/role. It does not connect to the real `GameCanvas` and does not handle game input.
- Button widgets only reference existing action ids supplied by the desktop JSON and validated through the existing registry checks.

## Deferred work

Future tasks can address a full display pipeline replacement, runtime editing/dragging, and real GameCanvas rendering. This task intentionally limits itself to card-internal widget rendering, button action integration, and page-level object plumbing.
