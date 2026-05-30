# TASK26 Component Deduplication Audit

## Scope

This audit is limited to `ui_qml/components` files used by the TASK26 desktop-card/mobile-desktop GUI direction. It does not change backend pipelines, command registry, render resources, action ids, or page routing.

## Design target

RELIC should move toward a mobile-desktop-like card system:

- mandatory I/O and safety modules remain present and coverage-checked;
- optional cards can be added, removed, moved, resized, recolored, skinned, or restyled;
- cards can host widgets such as text, metric, button, image, HUD, and GameCanvas placeholders;
- QML remains a rendering layer, while Python validates layout, pipeline coverage, actions, assets, and required cards.

## Findings

### 1. HomeCardSlotPreview vs TrainingCardSlotPreview

These two components are the strongest duplication.

Common fields:

- `slotIndex`
- `cardId`
- `cardType`
- `cardTitleText`
- `cardSubtitleText`
- `requiredCard`
- `lockedCard`
- `widgetCount`
- `actionIdsText`
- `sourceRootsText`
- `firstWidgetLabelsText`

Training adds:

- `rectText`
- `placeholder`
- `roleText`

Home uses numeric rectangle fields:

- `modelX`
- `modelY`
- `modelWidth`
- `modelHeight`

Conclusion: merge the internal rendering into `DesktopCardSlotPreview.qml`, keep `HomeCardSlotPreview.qml` and `TrainingCardSlotPreview.qml` as compatibility wrappers. This reduces duplicated layout code while preserving existing page-specific APIs and tests.

### 2. HomeCardSlotsPreview vs TrainingCardSlotsPreview

These are structurally similar but not good deletion targets yet.

Home has 4 slots and no placeholder/role fields. Training has 7 slots and needs GameCanvas placeholder semantics. Current tests and QML bindings are fixed-slot, so a full merge would either introduce dynamic structures or a large property surface.

Conclusion: keep both for now. Later, after official Home/Training page pilots are stable, introduce a page-specific wrapper over a common fixed-slot host.

### 3. HomeRenderModelPreview vs TrainingRenderModelPreview

These duplicate the same card shell and ConfigTextWidget display pattern. Training has extra fields for placeholders, GameCanvas, Safe Stop, Slots, and Injection.

Conclusion: merge internal rendering into `RenderModelSummaryPreview.qml`, keep the two page-specific wrappers for stable public APIs and test compatibility.

### 4. DesignCard / DesignPanel / DesignMetricCard

These overlap visually but do not have identical roles.

- `DesignCard.qml` is the TASK26 desktop card shell.
- `DesignPanel.qml` is a legacy/design-pack panel container.
- `DesignMetricCard.qml` is a legacy metric card.
- `ConfigMetricWidget.qml` is a widget inside cards.

Conclusion: do not merge now. `DesignCard.qml` should become the card-system base; legacy components should remain until official fallback pages are stable.

### 5. ConfigTextWidget / ConfigMetricWidget

These are related but not duplicates.

`ConfigMetricWidget` adds level/freshness coloring; `ConfigTextWidget` is neutral text/value display.

Conclusion: keep both. A future base text/value primitive is possible, but it is not needed before page replacement.

### 6. ConfigButtonWidget / DesignButton

These are not duplicates.

- `DesignButton.qml` is a general styled button component.
- `ConfigButtonWidget.qml` is action-aware and can invoke action ids through the bridge.

Conclusion: keep both. The mobile-desktop card system needs both visual button styling and action-safe button widgets.

### 7. GameCanvas

`GameCanvas.qml` is a true runtime/game rendering component. It should not be merged with card previews. It should later be wrapped by `ConfigGameWidget` or `GameCanvasCard`.

Conclusion: do not modify or merge.

## Patch strategy

This patch performs a safe first-stage consolidation:

1. Adds `DesktopCardSlotPreview.qml`.
2. Rewrites `HomeCardSlotPreview.qml` as a wrapper around `DesktopCardSlotPreview`.
3. Rewrites `TrainingCardSlotPreview.qml` as a wrapper around `DesktopCardSlotPreview`.
4. Adds `RenderModelSummaryPreview.qml`.
5. Rewrites `HomeRenderModelPreview.qml` as a wrapper around `RenderModelSummaryPreview`.
6. Rewrites `TrainingRenderModelPreview.qml` as a wrapper around `RenderModelSummaryPreview`.

No existing public component filenames are removed. That is intentional: current tests and page QML import these names directly.

## Safe deletion conclusion

No component should be physically deleted in this patch.

Deletion can be considered later only after:

- HomePage and TrainingPage desktop pilots are stable;
- all page-specific wrappers are replaced by common components;
- tests no longer check the old file names;
- legacy fallback pages remain available.

## Pipeline coverage conclusion

Component merging must not replace pipeline coverage. Required cards, required fields, required buttons, locked modules, and `live.safe_stop` accessibility must remain enforced by Python tools such as:

- `tools/check_gui_pipeline_coverage.py`
- `tools/check_task26_contracts.py`

The correct rule is:

- mandatory I/O/safety modules are cardified but cannot disappear;
- optional decoration/content modules may be added or removed;
- both types are visually customizable, but only optional modules are removable.

This preserves the mobile-desktop user experience without breaking RELIC runtime, session, calibration, training, diagnostics, and safety workflows.
