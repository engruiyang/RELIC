# TASK26F Training Contract（TASK26F-1）

## Scope

TASK26F-1 hardens the Training desktop prototype contract and exposes a summary preview in DeveloperLab. It still does not modify `TrainingPage.qml`, does not connect `GameCanvas`, does not implement `TrainingDesktopPage.qml`, and does not execute configured `source` or `action_id` values.

## Stable fields

The following fields are considered stable for the Training render-model prototype and contract gate:

- `sessionState.session_active`
- `sessionState.current_session_id`
- `sessionState.session_elapsed_ms`
- `runtimeSnapshot.stream_alive`
- `runtimeSnapshot.attention`
- `runtimeSnapshot.attention_age_ms`
- `runtimeSnapshot.gyro_x`
- `runtimeSnapshot.gyro_y`
- `runtimeSnapshot.gyro_z`
- `runtimeSnapshot.gyro_age_ms`
- `runtimeSnapshot.warning_flags`
- `runtimeSnapshot.error_flags`

These fields remain declarative in TASK26F-1. The builder and DeveloperLab preview summarize them but do not evaluate them.

## Pending validation fields

The following fields are prototype placeholders and must be validated against the bridge/facade payload contract before any real Training desktop migration:

- `gameHudJson.status`
- `gameHudJson.score`
- `gameHudJson.focus_index`
- `gameViewJson.status`
- `gameViewJson.scene`
- calibration status related fields, including final naming for calibration usability and latest calibration identity

`training_page.desktop_demo.json` marks the current game HUD placeholder fields with `contract_status: pending_bridge_validation` / `prototype: true`.

## Required actions

The following actions must remain available in any future Training cardized path:

- `session.start`
- `session.stop`
- `session.status`
- `live.safe_stop`
- `calibration.status`
- `game.status`
- `diagnostics.refresh`

`live.safe_stop` remains safety-critical and must remain accessible even while Training desktop support is only a prototype.

## Legacy / existing-QML-only behavior

- `training.readiness` is a legacy existing-QML-only readiness result. It is not a command-registry/native action in TASK26F-1.
- Current readiness behavior must continue to use the legacy TrainingPage path until a later phase explicitly migrates it behind a validated fallback.

## GameCanvasCard / ConfigGameWidget future contract draft

- `game_canvas_card` is currently a placeholder only.
- A later phase must implement a dedicated `ConfigGameWidget` or `GameCanvasCard`; it must not be folded into a generic metric/text widget.
- `GameCanvas` must preserve legacy fallback and existing event routing semantics.
- TASK26F-1 does not connect `GameCanvas` QML and does not alter `ui_qml/components/GameCanvas.qml`.
- Any future GameCanvas migration must be validated separately from the ordinary card/widget render-model pipeline.

## Unsupported Training slots/injection

Training slots and injection payloads are intentionally unsupported in TASK26F-1. CLI requests for `--page training --slots` or `--page training --injection` must fail with a clear error instead of producing partial payloads.
