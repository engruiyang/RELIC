# TASK26F-0A Training Migration Audit

## Scope

TASK26F-0A only audits the existing training page and adds an offline desktop demo/render-model prototype. It does not modify `TrainingPage.qml`, does not attach a real QML desktop page, does not migrate `GameCanvas`, and does not execute configured `source` or `action_id` values.

## Existing TrainingPage major regions

The current `ui_qml/pages/TrainingPage.qml` is a single legacy page with these major areas:

1. **Page title / header**
   - `PageHeader` displays `Training Page` and the readiness/session/game command subtitle.
2. **Design pack status**
   - Shows `renderResourcesObj.design_pack`, `gameStyleObj`, `effectStyleObj`, and panel token status.
3. **Training readiness / gate**
   - Shows `current_user_id`, profile loaded state, last calibration id, calibration usability, formal training allowed, and readiness reason.
   - `training.readiness` is represented as a QML-local result object after checking profile/calibration state.
4. **Training action area**
   - Buttons call existing QML functions for refresh readiness, start session, stop session, safe stop, session status, and game status.
5. **Game selection**
   - Exposes existing `trace_lock` only and calls `game.select` through the existing native facade path.
6. **TraceLock difficulty controls**
   - Uses existing selectors and buttons to call `game.difficulty` through the existing native facade path.
7. **Session status area**
   - Displays session active/id/elapsed/latest report/last status and latest session action result.
8. **Runtime / stream status area**
   - Displays quality/control state, focus/attention, attention freshness, gyro freshness, warning flags, and error flags.
9. **Game HUD area**
   - Displays score, combo, level, difficulty, accuracy, omissions, false actions, time left, and TraceLock status fields from `gameHudObj`/`controlStateObj`.
10. **GameCanvas / game preview area**
    - Embeds the existing `GameCanvas` and passes the current game view, bridge reference, theme/style objects, and render resources.
11. **Diagnostics / feedback area**
    - Shows the latest action result text and page command summary.
12. **PageFeedbackPanel / command feedback**
    - Shows selected command/action status and latest `controlStateObj` command result/error values.

## Checked action_id values

| action_id | Status | Evidence / notes |
| --- | --- | --- |
| `session.start` | registry native action | `command_registry.py` maps training start to native action `session.start`; `TrainingPage.qml` calls it in `startTrainingSession()`. |
| `session.stop` | registry native action | `command_registry.py` maps training stop to native action `session.stop`; `TrainingPage.qml` calls it in `stopTrainingSession()`. |
| `session.status` | registry native action | `command_registry.py` maps training status to native action `session.status`; `TrainingPage.qml` calls it in `querySessionStatus()`. |
| `training.readiness` | existing-qml-only | `TrainingPage.qml` constructs this result locally in `refreshReadiness()`; no registry native action was found. |
| `game.status` | registry native action | `command_registry.py` maps game status to native action `game.status`; `TrainingPage.qml` calls it in `queryGameStatus()`. |
| `calibration.status` | registry native action | `command_registry.py` maps calibration status to native action `calibration.status`; `TrainingPage.qml` calls it during readiness refresh. |
| `live.safe_stop` | native whitelist / existing facade path | Not present as a command-registry native action, but existing GUI facade exposes it and TASK26 desktop coverage treats it as a native action id. `TrainingPage.qml` calls it in `safeStop()`. |
| `diagnostics.refresh` | registry native action | `command_registry.py` maps diagnostics refresh to native action `diagnostics.refresh`; the current TrainingPage does not show a diagnostics refresh button. |

Additional existing QML/facade actions observed but not used in the TASK26F-0A demo config because they are outside the required action list and are not command-registry native ids: `game.select` and `game.difficulty`.

## Existing data source root objects

| Root | Existing status / mapping note |
| --- | --- |
| `appState` | Bridge/root JSON source; TrainingPage receives parsed values via `appStateObj`, mainly for current user fallback. |
| `runtimeSnapshot` | Bridge/root JSON source; TrainingPage receives parsed values via `runtimeObj`, including attention/gyro freshness and warning/error flags. |
| `sessionState` | Bridge/root JSON source; TrainingPage displays session-like values through `controlStateObj` today, while TASK26 config uses `sessionState.*` to match the existing desktop schema root. |
| `controlState` / `controlStateJson` | Bridge/root JSON source; TrainingPage receives parsed values via `controlStateObj` for current user, profile/calibration flags, session fields, latest commands, and behavior sample count. |
| `gameHud` / `gameHudJson` | Bridge/root JSON source; TrainingPage receives parsed values via `gameHudObj`. The prototype uses `gameHudJson.status`, `gameHudJson.score`, and `gameHudJson.focus_index` as placeholders to be verified in a later phase. |
| `gameView` / `gameViewJson` | Bridge/root JSON source; TrainingPage receives parsed values via `gameViewObj`; `GameCanvas` uses the current game view object. |
| `renderResourcesObj` / `renderResourcesJson` | Design pack/render resource root; TrainingPage passes `renderResourcesObj` into design components, `GameCanvas`, and `PageFeedbackPanel`. |

## Core chains that must not be broken by cardization

- **safe stop**: `live.safe_stop` must remain accessible even if cards are introduced later; this is safety-critical and currently follows the existing native/facade path.
- **session start / stop**: `session.start` includes readiness and game-selection gates in current QML before invoking the action; `session.stop` updates session results.
- **session status**: `session.status` is the existing read-only check for the session state display.
- **attention freshness**: `runtimeSnapshot.attention`, `attention_fresh`, and `attention_age_ms` are core readiness/quality signals.
- **gyro freshness**: `runtimeSnapshot.gyro_x/y/z`, `gyro_fresh`, and `gyro_age_ms` must remain visible for live input confidence.
- **runtime warning / error**: `runtimeSnapshot.warning_flags` and `runtimeSnapshot.error_flags` are diagnostic guardrails.
- **calibration status**: Readiness depends on loaded profile/calibration usability and `calibration.status` checks.
- **game status**: `game.status`, current game id, selected TraceLock state, and HUD status must remain inspectable.
- **GameCanvas / game HUD**: The existing `GameCanvas` bridge/event path and HUD data must be migrated separately; this phase only declares a placeholder card.

## Recommended training card split

TASK26F-0A introduces the following offline card split in `training_page.desktop_demo.json`:

1. `training_control_card` — required/locked safety and session controls.
2. `session_card` — required/locked session active/id/elapsed state.
3. `runtime_io_card` — required/locked stream, attention, and gyro freshness state.
4. `calibration_status_card` — required/locked calibration usability/status coverage.
5. `game_hud_card` — required/locked HUD summary with placeholder `gameHudJson.*` fields that need later validation.
6. `game_canvas_card` — required/locked `type: game` placeholder only; no `GameCanvas` QML hookup in this phase.
7. `diagnostics_summary_card` — required/locked runtime warnings/errors plus diagnostics refresh action.

## Deferred validation items

- `gameHudJson.status`, `gameHudJson.score`, and `gameHudJson.focus_index` are intentionally conservative placeholders for the prototype; later TASK26F phases must verify the final HUD field contract against bridge/facade payloads.
- `sessionState.*` is the intended desktop schema root for session fields; current legacy TrainingPage displays several session values through `controlStateObj`, so later migration must preserve legacy fallback behavior while normalizing sources.
- `GameCanvas` migration must be handled as a separate `ConfigGameWidget` or `GameCanvasCard` design and must preserve pointer event routing and existing game-client behavior.

## TASK26F-1 contract hardening note

TASK26F-1 adds a Training contract summary for DeveloperLab preview only. This does not alter the original audit boundary: `TrainingPage.qml` remains unchanged, `GameCanvas` remains on the legacy path, and configured `source` / `action_id` values remain declarative.
