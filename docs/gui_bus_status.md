# GUI Bus Status Baseline (TASK20-S)

This document locks the current GUI integration boundary for the smoke-shell phase.

1. Platform live stream enters `RuntimeSnapshot`.
2. `GuiFacade` / `GuiBridge` expose `runtimeSnapshot`, `sessionState`, and `gameHudJson` to QML.
3. QML is display-only for bus status and does not directly access DataCenter.
4. QML does not judge hit/miss (QML 不判断命中).
5. QML does not generate `GameEvent` (QML 不生成 GameEvent).
6. `GameInputEvent` enters `GameClient` from user click coordinates.
7. `GameClient` outputs `GameViewState` / `GameEvent` / `BehaviorSample`.
8. `GameEvent` can flow into PlatformReporter mock pipeline.
9. TraceLock is the teammate integration reference sample.
10. Main program page and mini-game training page split belongs to follow-up `TASK23`.
11. Safe recovery of `GameCanvas` belongs to follow-up `TASK24`.
12. Asset pack system belongs to follow-up `TASK25`.
