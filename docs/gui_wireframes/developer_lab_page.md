# Developer_Lab Page Wireframe (Low Fidelity)

> This is a wireframe + observability spec, not a claim of fully implemented UX.

```text
+--------------------------------------------------------------+
| Header: Developer_Lab                                            |
+-------------------------+------------------------------------+
| Left / Summary Panel    | Right / List + Detail + Result    |
| - key fields            | - list area                        |
| - workflow hint         | - detail area                      |
| - actions/buttons       | - action result area               |
+-------------------------+------------------------------------+
| Empty State / Guidance / Main Flow Note                      |
+--------------------------------------------------------------+
```

## Regions / Fields
- Summary panel: current_user_id, profile/calibration/session status (page-specific).
- List panel: action result items.
- Detail panel: selected/latest detail.
- Result panel: action status/message.

## Buttons and action_id
- Home: app.refresh_now + navigation to User/Calibration/Training/Report.
- User: user.list, user.create, user.load, user.load_current.
- Calibration: calibration.status, calibration.list, calibration.latest, calibration.start.
- Training: session.start, session.stop, game.status.
- Report: report.refresh, report.list, report.show.
- Diagnostics: diagnostics.refresh (if present).
- Developer Lab: devlab.run.

## Empty state copy
- "No action result yet" / "No items yet" / "Select an item to view details".

## Action result location
- Bottom Result panel of each page, backed by page action result object.

## Main flow
- Home -> User/Profile -> Calibration -> Training -> Report.
