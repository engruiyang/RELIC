# TASK26H-5E User Profile Control-State Binding

This patch fixes the remaining User page profile display issue. The database and `user.load` / `user.show_profile` action pipeline were already returning profile data, but the desktop cards still relied on `controlStateJson` fields that were incomplete or missing.

## Fixes

- `GuiFacade.get_control_state()` now builds a baseline user profile context for the current user.
- Profile fields are no longer available only after the last action result.
- `attention_low_threshold`, `attention_high_threshold`, `preferred_game_id`, and `difficulty_level` are exposed directly in `controlStateJson`.
- `attention_baseline`, `calibration_usable`, and `gyro_noise_rms` continue to come from the bound calibration profile.
- User layout payload is hydrated from `controlStateJson` values before being exposed through `renderResourcesJson`, so desktop card widgets can show values even when QML source lookup is imperfect.
- Core-control mode now keeps a GUI-side current-user override, so selecting/loading a user updates GUI state even when the core source itself is read-only.

## Scope

No new button flow is introduced. No command registry changes are required. User profile data still uses the existing `GuiFacade`, `GuiBridge.controlStateJson`, and desktop card widget pipeline.
