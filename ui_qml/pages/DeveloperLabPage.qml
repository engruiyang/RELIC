import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    property var guiBridge: null
    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var renderResourcesObj: ({})
    property var controlStateObj: ({})
    property string commandSummary: ""
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""
    property string selectedCliReference: ""

    function pick(id, status, mode, cli) {
        selectedCommandId = id
        selectedStatus = status
        selectedExecutionMode = mode
        selectedNativeActionId = ""
        selectedCliReference = cli
    }

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    function task26PayloadValue(key, fallbackValue) {
        var resources = root.renderResourcesObj || ({})
        var payload = resources.task26_home_slots_payload || ({})
        if (payload[key] === undefined || payload[key] === null) {
            return fallbackValue
        }
        return payload[key]
    }

    function task26TrainingSummary() {
        var resources = renderResourcesObj || ({})
        return resources.task26_training_summary || ({})
    }

    function task26TrainingValue(key, fallbackValue) {
        var summary = task26TrainingSummary()
        if (summary[key] === undefined || summary[key] === null) {
            return fallbackValue
        }
        return summary[key]
    }

    function task26TrainingListValue(key, fallbackValue) {
        var v = task26TrainingValue(key, [])
        if (!v || v.length === undefined || v.length === 0) {
            return fallbackValue
        }
        return v.join(", ")
    }

    function task26TrainingSlotsPayload() {
        var resources = renderResourcesObj || ({})
        return resources.task26_training_slots_payload || ({})
    }

    function task26TrainingSlotValue(key, fallbackValue) {
        var payload = task26TrainingSlotsPayload()
        if (payload[key] === undefined || payload[key] === null) {
            return fallbackValue
        }
        return payload[key]
    }

    function task26HomeLayoutPayload() {
        var resources = root.renderResourcesObj || ({})
        return resources.task26_home_layout_payload || ({})
    }

    function task26HomeLayoutValue(key, fallbackValue) {
        var payload = task26HomeLayoutPayload()
        if (payload[key] === undefined || payload[key] === null) {
            return fallbackValue
        }
        return payload[key]
    }

    function task26TrainingLayoutPayload() {
        var resources = root.renderResourcesObj || ({})
        return resources.task26_training_layout_payload || ({})
    }

    function task26TrainingLayoutValue(key, fallbackValue) {
        var payload = task26TrainingLayoutPayload()
        if (payload[key] === undefined || payload[key] === null) {
            return fallbackValue
        }
        return payload[key]
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: (root.designThemeObj.colors && root.designThemeObj.colors.background) ? root.designThemeObj.colors.background : "#F8FAFC"
    }

    Flickable {
        id: developerLabScroll
        anchors.fill: parent
        clip: true
        contentWidth: width
        contentHeight: developerLabContent.implicitHeight + 16
        boundsBehavior: Flickable.StopAtBounds

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }

        Column {
            id: developerLabContent
            width: developerLabScroll.width
            spacing: 6

            PageHeader {
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            headerStyleObj: root.componentStyleObj.header || ({})
            titleText: "Developer Lab"
            subtitleText: "Advanced/manual/copy_only command catalog"
        }

        GroupBox {
            title: "Developer Lab Actions"
            Column {
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "runtime.core_debug_mock"; onClicked: pick("runtime.core_debug_mock", "active", "copy_only", "python -m ui_cli.run_core_debug --bridge mock") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "runtime.core_debug_live"; onClicked: pick("runtime.core_debug_live", "active", "copy_only", "python -m ui_cli.run_core_debug --bridge live --host 127.0.0.1 --port 8000") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "game.debug_mock"; onClicked: pick("game.debug_mock", "active", "copy_only", "python -m ui_cli.run_game_debug --bridge mock ...") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "game.debug_live"; onClicked: pick("game.debug_live", "active", "copy_only", "python -m ui_cli.run_game_debug --bridge live ...") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "game.debug_live_record_pipeline"; onClicked: pick("game.debug_live_record_pipeline", "active", "copy_only", "python -m ui_cli.run_game_debug --bridge live ... --record-pipeline-jsonl ...") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "developer.task6b_record_mock"; onClicked: pick("developer.task6b_record_mock", "active", "copy_only", "bash scripts/task6b_record.sh mock demo 180 baseline") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "developer.task6b_record_live"; onClicked: pick("developer.task6b_record_live", "active", "copy_only", "bash scripts/task6b_record.sh live TEST 180 real_trial") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "developer.task6b_evaluate"; onClicked: pick("developer.task6b_evaluate", "active", "copy_only", "python -m ui_cli.evaluate_task6b ...") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "developer.task6b_tune"; onClicked: pick("developer.task6b_tune", "active", "copy_only", "python -m ui_cli.tune_task6b ...") }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "developer.task6b_calibrate"; onClicked: pick("developer.task6b_calibrate", "active", "copy_only", "python -m ui_cli.calibrate_task6b ...") }
            }
        }

        GroupBox {
            title: "TASK26 Desktop Card Preview"

            CardHostPreview {
                id: task26CardPreview
                width: parent.width
                height: 420
                guiBridge: root.guiBridge
            }
        }



        GroupBox {
            title: "TASK26 Home Render Model Preview"

            HomeRenderModelPreview {
                id: task26HomeRenderModelPreview
                width: parent.width
                height: 360
                pageId: "home"
                cardCount: 4
                widgetCount: 10
                requiredCardCount: 2
                lockedCardCount: 2
                actionsText: "app.refresh_now, live.safe_stop"
                sourceRootsText: "gameHudJson, renderResourcesJson, runtimeSnapshot, sessionState"
                cardIdsText: "runtime_io_card, quick_actions_card, recent_session_card, relic_identity_card"
            }
        }



        GroupBox {
            title: "TASK26 Home Card Slots Preview"

            HomeCardSlotsPreview {
                id: task26HomeCardSlotsPreview
                width: parent.width
                height: 520
                slot1CardId: task26PayloadValue("slot1_card_id", "runtime_io_card")
                slot2CardId: task26PayloadValue("slot2_card_id", "quick_actions_card")
                slot3CardId: task26PayloadValue("slot3_card_id", "recent_session_card")
                slot4CardId: task26PayloadValue("slot4_card_id", "relic_identity_card")
                slot1CardType: task26PayloadValue("slot1_card_type", "runtime")
                slot2CardType: task26PayloadValue("slot2_card_type", "actions")
                slot3CardType: task26PayloadValue("slot3_card_type", "session")
                slot4CardType: task26PayloadValue("slot4_card_type", "identity")
                slot1Title: task26PayloadValue("slot1_title", "Runtime I/O")
                slot2Title: task26PayloadValue("slot2_title", "Quick Actions")
                slot3Title: task26PayloadValue("slot3_title", "Recent Session")
                slot4Title: task26PayloadValue("slot4_title", "RELIC Identity")
                slot1Subtitle: task26PayloadValue("slot1_subtitle", "Connection and stream health")
                slot2Subtitle: task26PayloadValue("slot2_subtitle", "Safety and refresh")
                slot3Subtitle: task26PayloadValue("slot3_subtitle", "Session summary")
                slot4Subtitle: task26PayloadValue("slot4_subtitle", "Brand and visual")
                slot1Required: task26PayloadValue("slot1_required", true)
                slot2Required: task26PayloadValue("slot2_required", true)
                slot3Required: task26PayloadValue("slot3_required", false)
                slot4Required: task26PayloadValue("slot4_required", false)
                slot1Locked: task26PayloadValue("slot1_locked", true)
                slot2Locked: task26PayloadValue("slot2_locked", true)
                slot3Locked: task26PayloadValue("slot3_locked", false)
                slot4Locked: task26PayloadValue("slot4_locked", false)
                slot1RectText: task26PayloadValue("slot1_rect_text", "x=10.0, y=10.0, w=386.0, h=290.0")
                slot2RectText: task26PayloadValue("slot2_rect_text", "x=404.0, y=10.0, w=386.0, h=290.0")
                slot3RectText: task26PayloadValue("slot3_rect_text", "x=10.0, y=308.0, w=584.0, h=290.0")
                slot4RectText: task26PayloadValue("slot4_rect_text", "x=798.0, y=10.0, w=386.0, h=588.0")
                slot1WidgetCount: task26PayloadValue("slot1_widget_count", 3)
                slot2WidgetCount: task26PayloadValue("slot2_widget_count", 2)
                slot3WidgetCount: task26PayloadValue("slot3_widget_count", 3)
                slot4WidgetCount: task26PayloadValue("slot4_widget_count", 2)
                slot1ActionIdsText: task26PayloadValue("slot1_action_ids_text", "n/a")
                slot2ActionIdsText: task26PayloadValue("slot2_action_ids_text", "app.refresh_now, live.safe_stop")
                slot3ActionIdsText: task26PayloadValue("slot3_action_ids_text", "n/a")
                slot4ActionIdsText: task26PayloadValue("slot4_action_ids_text", "n/a")
                slot1SourceRootsText: task26PayloadValue("slot1_source_roots_text", "runtimeSnapshot")
                slot2SourceRootsText: task26PayloadValue("slot2_source_roots_text", "n/a")
                slot3SourceRootsText: task26PayloadValue("slot3_source_roots_text", "gameHudJson, sessionState")
                slot4SourceRootsText: task26PayloadValue("slot4_source_roots_text", "renderResourcesJson")
                slot1FirstWidgetLabelsText: task26PayloadValue("slot1_first_widget_labels_text", "Runtime, Stream, Attention")
                slot2FirstWidgetLabelsText: task26PayloadValue("slot2_first_widget_labels_text", "Refresh, Safe Stop")
                slot3FirstWidgetLabelsText: task26PayloadValue("slot3_first_widget_labels_text", "Active, Session ID, HUD")
                slot4FirstWidgetLabelsText: task26PayloadValue("slot4_first_widget_labels_text", "Identity, Tagline")
            }
        }

        GroupBox {
            title: "TASK26 Home Desktop Layout Preview"
            DesktopLayoutPreview {
                id: task26HomeDesktopLayoutPreview
                layoutPayload: task26HomeLayoutPayload()
                width: parent.width
                height: 560
                previewTitle: "Home Desktop Layout Preview"
                previewSubtitle: "TASK26 grid position and size preview"
                pageId: task26HomeLayoutValue("page_id", "home")
                modelPageWidth: task26HomeLayoutValue("page_width", 1200)
                modelPageHeight: task26HomeLayoutValue("page_height", 800)
                cardCount: task26HomeLayoutValue("card_count", 0)
                payloadStatusText: (root.renderResourcesObj || ({})).task26_home_layout_status || "n/a"
                payloadSourceText: (root.renderResourcesObj || ({})).task26_home_layout_source || "n/a"
                card1Visible: task26HomeLayoutValue("card1_visible", false)
                card1Id: task26HomeLayoutValue("card1_id", "")
                card1Type: task26HomeLayoutValue("card1_type", "")
                card1Title: task26HomeLayoutValue("card1_title", "")
                card1Subtitle: task26HomeLayoutValue("card1_subtitle", "")
                card1X: task26HomeLayoutValue("card1_x", 0)
                card1Y: task26HomeLayoutValue("card1_y", 0)
                card1Width: task26HomeLayoutValue("card1_width", 0)
                card1Height: task26HomeLayoutValue("card1_height", 0)
                card1Required: task26HomeLayoutValue("card1_required", false)
                card1Locked: task26HomeLayoutValue("card1_locked", false)
                card1WidgetCount: task26HomeLayoutValue("card1_widget_count", 0)
                card1ActionIdsText: task26HomeLayoutValue("card1_action_ids_text", "n/a")
                card1SourceRootsText: task26HomeLayoutValue("card1_source_roots_text", "n/a")
                card1FirstWidgetLabelsText: task26HomeLayoutValue("card1_first_widget_labels_text", "n/a")
                card1Placeholder: task26HomeLayoutValue("card1_placeholder", false)
                card1RoleText: task26HomeLayoutValue("card1_role", "")
                card2Visible: task26HomeLayoutValue("card2_visible", false)
                card2Id: task26HomeLayoutValue("card2_id", "")
                card2Type: task26HomeLayoutValue("card2_type", "")
                card2Title: task26HomeLayoutValue("card2_title", "")
                card2Subtitle: task26HomeLayoutValue("card2_subtitle", "")
                card2X: task26HomeLayoutValue("card2_x", 0)
                card2Y: task26HomeLayoutValue("card2_y", 0)
                card2Width: task26HomeLayoutValue("card2_width", 0)
                card2Height: task26HomeLayoutValue("card2_height", 0)
                card2Required: task26HomeLayoutValue("card2_required", false)
                card2Locked: task26HomeLayoutValue("card2_locked", false)
                card2WidgetCount: task26HomeLayoutValue("card2_widget_count", 0)
                card2ActionIdsText: task26HomeLayoutValue("card2_action_ids_text", "n/a")
                card2SourceRootsText: task26HomeLayoutValue("card2_source_roots_text", "n/a")
                card2FirstWidgetLabelsText: task26HomeLayoutValue("card2_first_widget_labels_text", "n/a")
                card2Placeholder: task26HomeLayoutValue("card2_placeholder", false)
                card2RoleText: task26HomeLayoutValue("card2_role", "")
                card3Visible: task26HomeLayoutValue("card3_visible", false)
                card3Id: task26HomeLayoutValue("card3_id", "")
                card3Type: task26HomeLayoutValue("card3_type", "")
                card3Title: task26HomeLayoutValue("card3_title", "")
                card3Subtitle: task26HomeLayoutValue("card3_subtitle", "")
                card3X: task26HomeLayoutValue("card3_x", 0)
                card3Y: task26HomeLayoutValue("card3_y", 0)
                card3Width: task26HomeLayoutValue("card3_width", 0)
                card3Height: task26HomeLayoutValue("card3_height", 0)
                card3Required: task26HomeLayoutValue("card3_required", false)
                card3Locked: task26HomeLayoutValue("card3_locked", false)
                card3WidgetCount: task26HomeLayoutValue("card3_widget_count", 0)
                card3ActionIdsText: task26HomeLayoutValue("card3_action_ids_text", "n/a")
                card3SourceRootsText: task26HomeLayoutValue("card3_source_roots_text", "n/a")
                card3FirstWidgetLabelsText: task26HomeLayoutValue("card3_first_widget_labels_text", "n/a")
                card3Placeholder: task26HomeLayoutValue("card3_placeholder", false)
                card3RoleText: task26HomeLayoutValue("card3_role", "")
                card4Visible: task26HomeLayoutValue("card4_visible", false)
                card4Id: task26HomeLayoutValue("card4_id", "")
                card4Type: task26HomeLayoutValue("card4_type", "")
                card4Title: task26HomeLayoutValue("card4_title", "")
                card4Subtitle: task26HomeLayoutValue("card4_subtitle", "")
                card4X: task26HomeLayoutValue("card4_x", 0)
                card4Y: task26HomeLayoutValue("card4_y", 0)
                card4Width: task26HomeLayoutValue("card4_width", 0)
                card4Height: task26HomeLayoutValue("card4_height", 0)
                card4Required: task26HomeLayoutValue("card4_required", false)
                card4Locked: task26HomeLayoutValue("card4_locked", false)
                card4WidgetCount: task26HomeLayoutValue("card4_widget_count", 0)
                card4ActionIdsText: task26HomeLayoutValue("card4_action_ids_text", "n/a")
                card4SourceRootsText: task26HomeLayoutValue("card4_source_roots_text", "n/a")
                card4FirstWidgetLabelsText: task26HomeLayoutValue("card4_first_widget_labels_text", "n/a")
                card4Placeholder: task26HomeLayoutValue("card4_placeholder", false)
                card4RoleText: task26HomeLayoutValue("card4_role", "")
                card5Visible: task26HomeLayoutValue("card5_visible", false)
                card5Id: task26HomeLayoutValue("card5_id", "")
                card5Type: task26HomeLayoutValue("card5_type", "")
                card5Title: task26HomeLayoutValue("card5_title", "")
                card5Subtitle: task26HomeLayoutValue("card5_subtitle", "")
                card5X: task26HomeLayoutValue("card5_x", 0)
                card5Y: task26HomeLayoutValue("card5_y", 0)
                card5Width: task26HomeLayoutValue("card5_width", 0)
                card5Height: task26HomeLayoutValue("card5_height", 0)
                card5Required: task26HomeLayoutValue("card5_required", false)
                card5Locked: task26HomeLayoutValue("card5_locked", false)
                card5WidgetCount: task26HomeLayoutValue("card5_widget_count", 0)
                card5ActionIdsText: task26HomeLayoutValue("card5_action_ids_text", "n/a")
                card5SourceRootsText: task26HomeLayoutValue("card5_source_roots_text", "n/a")
                card5FirstWidgetLabelsText: task26HomeLayoutValue("card5_first_widget_labels_text", "n/a")
                card5Placeholder: task26HomeLayoutValue("card5_placeholder", false)
                card5RoleText: task26HomeLayoutValue("card5_role", "")
                card6Visible: task26HomeLayoutValue("card6_visible", false)
                card6Id: task26HomeLayoutValue("card6_id", "")
                card6Type: task26HomeLayoutValue("card6_type", "")
                card6Title: task26HomeLayoutValue("card6_title", "")
                card6Subtitle: task26HomeLayoutValue("card6_subtitle", "")
                card6X: task26HomeLayoutValue("card6_x", 0)
                card6Y: task26HomeLayoutValue("card6_y", 0)
                card6Width: task26HomeLayoutValue("card6_width", 0)
                card6Height: task26HomeLayoutValue("card6_height", 0)
                card6Required: task26HomeLayoutValue("card6_required", false)
                card6Locked: task26HomeLayoutValue("card6_locked", false)
                card6WidgetCount: task26HomeLayoutValue("card6_widget_count", 0)
                card6ActionIdsText: task26HomeLayoutValue("card6_action_ids_text", "n/a")
                card6SourceRootsText: task26HomeLayoutValue("card6_source_roots_text", "n/a")
                card6FirstWidgetLabelsText: task26HomeLayoutValue("card6_first_widget_labels_text", "n/a")
                card6Placeholder: task26HomeLayoutValue("card6_placeholder", false)
                card6RoleText: task26HomeLayoutValue("card6_role", "")
                card7Visible: task26HomeLayoutValue("card7_visible", false)
                card7Id: task26HomeLayoutValue("card7_id", "")
                card7Type: task26HomeLayoutValue("card7_type", "")
                card7Title: task26HomeLayoutValue("card7_title", "")
                card7Subtitle: task26HomeLayoutValue("card7_subtitle", "")
                card7X: task26HomeLayoutValue("card7_x", 0)
                card7Y: task26HomeLayoutValue("card7_y", 0)
                card7Width: task26HomeLayoutValue("card7_width", 0)
                card7Height: task26HomeLayoutValue("card7_height", 0)
                card7Required: task26HomeLayoutValue("card7_required", false)
                card7Locked: task26HomeLayoutValue("card7_locked", false)
                card7WidgetCount: task26HomeLayoutValue("card7_widget_count", 0)
                card7ActionIdsText: task26HomeLayoutValue("card7_action_ids_text", "n/a")
                card7SourceRootsText: task26HomeLayoutValue("card7_source_roots_text", "n/a")
                card7FirstWidgetLabelsText: task26HomeLayoutValue("card7_first_widget_labels_text", "n/a")
                card7Placeholder: task26HomeLayoutValue("card7_placeholder", false)
                card7RoleText: task26HomeLayoutValue("card7_role", "")
            }
        }
        GroupBox {
            title: "TASK26 Training Render Model Preview"

            TrainingRenderModelPreview {
                id: task26TrainingRenderModelPreview
                width: parent.width
                height: 420
                pageId: task26TrainingValue("page_id", "training")
                cardCount: task26TrainingValue("card_count", 0)
                widgetCount: task26TrainingValue("widget_count", 0)
                requiredCardsText: task26TrainingListValue("required_card_ids", "n/a")
                actionsText: task26TrainingListValue("action_ids", "n/a")
                sourceRootsText: task26TrainingListValue("source_roots", "n/a")
                placeholderSourcesText: task26TrainingListValue("placeholder_sources", "n/a")
                gameCanvasStatusText: task26TrainingValue("game_canvas_card_status", "n/a")
                safeStopPresent: task26TrainingValue("safe_stop_present", false)
                slotsSupportedText: task26TrainingValue("training_slots_supported", false) ? "true" : "false"
                injectionSupportedText: task26TrainingValue("training_injection_supported", false) ? "true" : "false"
            }
        }

        GroupBox {
            title: "TASK26 Training Card Slots Preview"

            TrainingCardSlotsPreview {
                id: task26TrainingCardSlotsPreview
                width: parent.width
                height: 760
                slotCount: task26TrainingSlotValue("slot_count", 7)
                slot1CardId: task26TrainingSlotValue("slot1_card_id", "training_control_card")
                slot1CardType: task26TrainingSlotValue("slot1_card_type", "")
                slot1Title: task26TrainingSlotValue("slot1_title", "training_control_card")
                slot1Subtitle: task26TrainingSlotValue("slot1_subtitle", "")
                slot1Required: task26TrainingSlotValue("slot1_required", true)
                slot1Locked: task26TrainingSlotValue("slot1_locked", true)
                slot1RectText: task26TrainingSlotValue("slot1_rect_text", "n/a")
                slot1WidgetCount: task26TrainingSlotValue("slot1_widget_count", 0)
                slot1ActionIdsText: task26TrainingSlotValue("slot1_action_ids_text", "n/a")
                slot1SourceRootsText: task26TrainingSlotValue("slot1_source_roots_text", "n/a")
                slot1FirstWidgetLabelsText: task26TrainingSlotValue("slot1_first_widget_labels_text", "n/a")
                slot1Placeholder: task26TrainingSlotValue("slot1_placeholder", false)
                slot1RoleText: task26TrainingSlotValue("slot1_role", "")
                slot2CardId: task26TrainingSlotValue("slot2_card_id", "session_card")
                slot2CardType: task26TrainingSlotValue("slot2_card_type", "")
                slot2Title: task26TrainingSlotValue("slot2_title", "session_card")
                slot2Subtitle: task26TrainingSlotValue("slot2_subtitle", "")
                slot2Required: task26TrainingSlotValue("slot2_required", true)
                slot2Locked: task26TrainingSlotValue("slot2_locked", true)
                slot2RectText: task26TrainingSlotValue("slot2_rect_text", "n/a")
                slot2WidgetCount: task26TrainingSlotValue("slot2_widget_count", 0)
                slot2ActionIdsText: task26TrainingSlotValue("slot2_action_ids_text", "n/a")
                slot2SourceRootsText: task26TrainingSlotValue("slot2_source_roots_text", "n/a")
                slot2FirstWidgetLabelsText: task26TrainingSlotValue("slot2_first_widget_labels_text", "n/a")
                slot2Placeholder: task26TrainingSlotValue("slot2_placeholder", false)
                slot2RoleText: task26TrainingSlotValue("slot2_role", "")
                slot3CardId: task26TrainingSlotValue("slot3_card_id", "runtime_io_card")
                slot3CardType: task26TrainingSlotValue("slot3_card_type", "")
                slot3Title: task26TrainingSlotValue("slot3_title", "runtime_io_card")
                slot3Subtitle: task26TrainingSlotValue("slot3_subtitle", "")
                slot3Required: task26TrainingSlotValue("slot3_required", true)
                slot3Locked: task26TrainingSlotValue("slot3_locked", true)
                slot3RectText: task26TrainingSlotValue("slot3_rect_text", "n/a")
                slot3WidgetCount: task26TrainingSlotValue("slot3_widget_count", 0)
                slot3ActionIdsText: task26TrainingSlotValue("slot3_action_ids_text", "n/a")
                slot3SourceRootsText: task26TrainingSlotValue("slot3_source_roots_text", "n/a")
                slot3FirstWidgetLabelsText: task26TrainingSlotValue("slot3_first_widget_labels_text", "n/a")
                slot3Placeholder: task26TrainingSlotValue("slot3_placeholder", false)
                slot3RoleText: task26TrainingSlotValue("slot3_role", "")
                slot4CardId: task26TrainingSlotValue("slot4_card_id", "calibration_status_card")
                slot4CardType: task26TrainingSlotValue("slot4_card_type", "")
                slot4Title: task26TrainingSlotValue("slot4_title", "calibration_status_card")
                slot4Subtitle: task26TrainingSlotValue("slot4_subtitle", "")
                slot4Required: task26TrainingSlotValue("slot4_required", true)
                slot4Locked: task26TrainingSlotValue("slot4_locked", true)
                slot4RectText: task26TrainingSlotValue("slot4_rect_text", "n/a")
                slot4WidgetCount: task26TrainingSlotValue("slot4_widget_count", 0)
                slot4ActionIdsText: task26TrainingSlotValue("slot4_action_ids_text", "n/a")
                slot4SourceRootsText: task26TrainingSlotValue("slot4_source_roots_text", "n/a")
                slot4FirstWidgetLabelsText: task26TrainingSlotValue("slot4_first_widget_labels_text", "n/a")
                slot4Placeholder: task26TrainingSlotValue("slot4_placeholder", false)
                slot4RoleText: task26TrainingSlotValue("slot4_role", "")
                slot5CardId: task26TrainingSlotValue("slot5_card_id", "game_hud_card")
                slot5CardType: task26TrainingSlotValue("slot5_card_type", "")
                slot5Title: task26TrainingSlotValue("slot5_title", "game_hud_card")
                slot5Subtitle: task26TrainingSlotValue("slot5_subtitle", "")
                slot5Required: task26TrainingSlotValue("slot5_required", true)
                slot5Locked: task26TrainingSlotValue("slot5_locked", true)
                slot5RectText: task26TrainingSlotValue("slot5_rect_text", "n/a")
                slot5WidgetCount: task26TrainingSlotValue("slot5_widget_count", 0)
                slot5ActionIdsText: task26TrainingSlotValue("slot5_action_ids_text", "n/a")
                slot5SourceRootsText: task26TrainingSlotValue("slot5_source_roots_text", "n/a")
                slot5FirstWidgetLabelsText: task26TrainingSlotValue("slot5_first_widget_labels_text", "n/a")
                slot5Placeholder: task26TrainingSlotValue("slot5_placeholder", false)
                slot5RoleText: task26TrainingSlotValue("slot5_role", "")
                slot6CardId: task26TrainingSlotValue("slot6_card_id", "game_canvas_card")
                slot6CardType: task26TrainingSlotValue("slot6_card_type", "")
                slot6Title: task26TrainingSlotValue("slot6_title", "game_canvas_card")
                slot6Subtitle: task26TrainingSlotValue("slot6_subtitle", "")
                slot6Required: task26TrainingSlotValue("slot6_required", true)
                slot6Locked: task26TrainingSlotValue("slot6_locked", true)
                slot6RectText: task26TrainingSlotValue("slot6_rect_text", "n/a")
                slot6WidgetCount: task26TrainingSlotValue("slot6_widget_count", 0)
                slot6ActionIdsText: task26TrainingSlotValue("slot6_action_ids_text", "n/a")
                slot6SourceRootsText: task26TrainingSlotValue("slot6_source_roots_text", "n/a")
                slot6FirstWidgetLabelsText: task26TrainingSlotValue("slot6_first_widget_labels_text", "n/a")
                slot6Placeholder: task26TrainingSlotValue("slot6_placeholder", false)
                slot6RoleText: task26TrainingSlotValue("slot6_role", "")
                slot7CardId: task26TrainingSlotValue("slot7_card_id", "diagnostics_summary_card")
                slot7CardType: task26TrainingSlotValue("slot7_card_type", "")
                slot7Title: task26TrainingSlotValue("slot7_title", "diagnostics_summary_card")
                slot7Subtitle: task26TrainingSlotValue("slot7_subtitle", "")
                slot7Required: task26TrainingSlotValue("slot7_required", true)
                slot7Locked: task26TrainingSlotValue("slot7_locked", true)
                slot7RectText: task26TrainingSlotValue("slot7_rect_text", "n/a")
                slot7WidgetCount: task26TrainingSlotValue("slot7_widget_count", 0)
                slot7ActionIdsText: task26TrainingSlotValue("slot7_action_ids_text", "n/a")
                slot7SourceRootsText: task26TrainingSlotValue("slot7_source_roots_text", "n/a")
                slot7FirstWidgetLabelsText: task26TrainingSlotValue("slot7_first_widget_labels_text", "n/a")
                slot7Placeholder: task26TrainingSlotValue("slot7_placeholder", false)
                slot7RoleText: task26TrainingSlotValue("slot7_role", "")
            }
        }
        GroupBox {
            title: "TASK26 Training Desktop Layout Preview"
            DesktopLayoutPreview {
                id: task26TrainingDesktopLayoutPreview
                layoutPayload: task26TrainingLayoutPayload()
                width: parent.width
                height: 620
                previewTitle: "Training Desktop Layout Preview"
                previewSubtitle: "TASK26 training grid position and size preview"
                pageId: task26TrainingLayoutValue("page_id", "training")
                modelPageWidth: task26TrainingLayoutValue("page_width", 1200)
                modelPageHeight: task26TrainingLayoutValue("page_height", 800)
                cardCount: task26TrainingLayoutValue("card_count", 0)
                payloadStatusText: (root.renderResourcesObj || ({})).task26_training_layout_status || "n/a"
                payloadSourceText: (root.renderResourcesObj || ({})).task26_training_layout_source || "n/a"
                card1Visible: task26TrainingLayoutValue("card1_visible", false)
                card1Id: task26TrainingLayoutValue("card1_id", "")
                card1Type: task26TrainingLayoutValue("card1_type", "")
                card1Title: task26TrainingLayoutValue("card1_title", "")
                card1Subtitle: task26TrainingLayoutValue("card1_subtitle", "")
                card1X: task26TrainingLayoutValue("card1_x", 0)
                card1Y: task26TrainingLayoutValue("card1_y", 0)
                card1Width: task26TrainingLayoutValue("card1_width", 0)
                card1Height: task26TrainingLayoutValue("card1_height", 0)
                card1Required: task26TrainingLayoutValue("card1_required", false)
                card1Locked: task26TrainingLayoutValue("card1_locked", false)
                card1WidgetCount: task26TrainingLayoutValue("card1_widget_count", 0)
                card1ActionIdsText: task26TrainingLayoutValue("card1_action_ids_text", "n/a")
                card1SourceRootsText: task26TrainingLayoutValue("card1_source_roots_text", "n/a")
                card1FirstWidgetLabelsText: task26TrainingLayoutValue("card1_first_widget_labels_text", "n/a")
                card1Placeholder: task26TrainingLayoutValue("card1_placeholder", false)
                card1RoleText: task26TrainingLayoutValue("card1_role", "")
                card2Visible: task26TrainingLayoutValue("card2_visible", false)
                card2Id: task26TrainingLayoutValue("card2_id", "")
                card2Type: task26TrainingLayoutValue("card2_type", "")
                card2Title: task26TrainingLayoutValue("card2_title", "")
                card2Subtitle: task26TrainingLayoutValue("card2_subtitle", "")
                card2X: task26TrainingLayoutValue("card2_x", 0)
                card2Y: task26TrainingLayoutValue("card2_y", 0)
                card2Width: task26TrainingLayoutValue("card2_width", 0)
                card2Height: task26TrainingLayoutValue("card2_height", 0)
                card2Required: task26TrainingLayoutValue("card2_required", false)
                card2Locked: task26TrainingLayoutValue("card2_locked", false)
                card2WidgetCount: task26TrainingLayoutValue("card2_widget_count", 0)
                card2ActionIdsText: task26TrainingLayoutValue("card2_action_ids_text", "n/a")
                card2SourceRootsText: task26TrainingLayoutValue("card2_source_roots_text", "n/a")
                card2FirstWidgetLabelsText: task26TrainingLayoutValue("card2_first_widget_labels_text", "n/a")
                card2Placeholder: task26TrainingLayoutValue("card2_placeholder", false)
                card2RoleText: task26TrainingLayoutValue("card2_role", "")
                card3Visible: task26TrainingLayoutValue("card3_visible", false)
                card3Id: task26TrainingLayoutValue("card3_id", "")
                card3Type: task26TrainingLayoutValue("card3_type", "")
                card3Title: task26TrainingLayoutValue("card3_title", "")
                card3Subtitle: task26TrainingLayoutValue("card3_subtitle", "")
                card3X: task26TrainingLayoutValue("card3_x", 0)
                card3Y: task26TrainingLayoutValue("card3_y", 0)
                card3Width: task26TrainingLayoutValue("card3_width", 0)
                card3Height: task26TrainingLayoutValue("card3_height", 0)
                card3Required: task26TrainingLayoutValue("card3_required", false)
                card3Locked: task26TrainingLayoutValue("card3_locked", false)
                card3WidgetCount: task26TrainingLayoutValue("card3_widget_count", 0)
                card3ActionIdsText: task26TrainingLayoutValue("card3_action_ids_text", "n/a")
                card3SourceRootsText: task26TrainingLayoutValue("card3_source_roots_text", "n/a")
                card3FirstWidgetLabelsText: task26TrainingLayoutValue("card3_first_widget_labels_text", "n/a")
                card3Placeholder: task26TrainingLayoutValue("card3_placeholder", false)
                card3RoleText: task26TrainingLayoutValue("card3_role", "")
                card4Visible: task26TrainingLayoutValue("card4_visible", false)
                card4Id: task26TrainingLayoutValue("card4_id", "")
                card4Type: task26TrainingLayoutValue("card4_type", "")
                card4Title: task26TrainingLayoutValue("card4_title", "")
                card4Subtitle: task26TrainingLayoutValue("card4_subtitle", "")
                card4X: task26TrainingLayoutValue("card4_x", 0)
                card4Y: task26TrainingLayoutValue("card4_y", 0)
                card4Width: task26TrainingLayoutValue("card4_width", 0)
                card4Height: task26TrainingLayoutValue("card4_height", 0)
                card4Required: task26TrainingLayoutValue("card4_required", false)
                card4Locked: task26TrainingLayoutValue("card4_locked", false)
                card4WidgetCount: task26TrainingLayoutValue("card4_widget_count", 0)
                card4ActionIdsText: task26TrainingLayoutValue("card4_action_ids_text", "n/a")
                card4SourceRootsText: task26TrainingLayoutValue("card4_source_roots_text", "n/a")
                card4FirstWidgetLabelsText: task26TrainingLayoutValue("card4_first_widget_labels_text", "n/a")
                card4Placeholder: task26TrainingLayoutValue("card4_placeholder", false)
                card4RoleText: task26TrainingLayoutValue("card4_role", "")
                card5Visible: task26TrainingLayoutValue("card5_visible", false)
                card5Id: task26TrainingLayoutValue("card5_id", "")
                card5Type: task26TrainingLayoutValue("card5_type", "")
                card5Title: task26TrainingLayoutValue("card5_title", "")
                card5Subtitle: task26TrainingLayoutValue("card5_subtitle", "")
                card5X: task26TrainingLayoutValue("card5_x", 0)
                card5Y: task26TrainingLayoutValue("card5_y", 0)
                card5Width: task26TrainingLayoutValue("card5_width", 0)
                card5Height: task26TrainingLayoutValue("card5_height", 0)
                card5Required: task26TrainingLayoutValue("card5_required", false)
                card5Locked: task26TrainingLayoutValue("card5_locked", false)
                card5WidgetCount: task26TrainingLayoutValue("card5_widget_count", 0)
                card5ActionIdsText: task26TrainingLayoutValue("card5_action_ids_text", "n/a")
                card5SourceRootsText: task26TrainingLayoutValue("card5_source_roots_text", "n/a")
                card5FirstWidgetLabelsText: task26TrainingLayoutValue("card5_first_widget_labels_text", "n/a")
                card5Placeholder: task26TrainingLayoutValue("card5_placeholder", false)
                card5RoleText: task26TrainingLayoutValue("card5_role", "")
                card6Visible: task26TrainingLayoutValue("card6_visible", false)
                card6Id: task26TrainingLayoutValue("card6_id", "")
                card6Type: task26TrainingLayoutValue("card6_type", "")
                card6Title: task26TrainingLayoutValue("card6_title", "")
                card6Subtitle: task26TrainingLayoutValue("card6_subtitle", "")
                card6X: task26TrainingLayoutValue("card6_x", 0)
                card6Y: task26TrainingLayoutValue("card6_y", 0)
                card6Width: task26TrainingLayoutValue("card6_width", 0)
                card6Height: task26TrainingLayoutValue("card6_height", 0)
                card6Required: task26TrainingLayoutValue("card6_required", false)
                card6Locked: task26TrainingLayoutValue("card6_locked", false)
                card6WidgetCount: task26TrainingLayoutValue("card6_widget_count", 0)
                card6ActionIdsText: task26TrainingLayoutValue("card6_action_ids_text", "n/a")
                card6SourceRootsText: task26TrainingLayoutValue("card6_source_roots_text", "n/a")
                card6FirstWidgetLabelsText: task26TrainingLayoutValue("card6_first_widget_labels_text", "n/a")
                card6Placeholder: task26TrainingLayoutValue("card6_placeholder", false)
                card6RoleText: task26TrainingLayoutValue("card6_role", "")
                card7Visible: task26TrainingLayoutValue("card7_visible", false)
                card7Id: task26TrainingLayoutValue("card7_id", "")
                card7Type: task26TrainingLayoutValue("card7_type", "")
                card7Title: task26TrainingLayoutValue("card7_title", "")
                card7Subtitle: task26TrainingLayoutValue("card7_subtitle", "")
                card7X: task26TrainingLayoutValue("card7_x", 0)
                card7Y: task26TrainingLayoutValue("card7_y", 0)
                card7Width: task26TrainingLayoutValue("card7_width", 0)
                card7Height: task26TrainingLayoutValue("card7_height", 0)
                card7Required: task26TrainingLayoutValue("card7_required", false)
                card7Locked: task26TrainingLayoutValue("card7_locked", false)
                card7WidgetCount: task26TrainingLayoutValue("card7_widget_count", 0)
                card7ActionIdsText: task26TrainingLayoutValue("card7_action_ids_text", "n/a")
                card7SourceRootsText: task26TrainingLayoutValue("card7_source_roots_text", "n/a")
                card7FirstWidgetLabelsText: task26TrainingLayoutValue("card7_first_widget_labels_text", "n/a")
                card7Placeholder: task26TrainingLayoutValue("card7_placeholder", false)
                card7RoleText: task26TrainingLayoutValue("card7_role", "")
            }
        }
        GroupBox {
            title: "Metadata"
            Column {
                Label { text: "execution_mode: " + s(selectedExecutionMode) }
                Label { text: "danger_level: advanced" }
                Label { text: "writes_db: possible" }
                Label { text: "connects_platform: possible" }
                Label { text: "generates_files: likely" }
                Label { text: "cli_reference: " + s(selectedCliReference) }
                Label { text: "copy_only / manual" }
            }
        }

        GroupBox {
            title: "Page Commands"
            Label {
                text: commandSummary
                wrapMode: Text.WordWrap
            }
        }

        PageFeedbackPanel {
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            feedbackStyleObj: root.componentStyleObj.feedback_panel || ({})
            pageId: "developer_lab"
            selectedCommandId: root.selectedCommandId
            selectedStatus: root.selectedStatus
            selectedExecutionMode: root.selectedExecutionMode
            selectedNativeActionId: root.selectedNativeActionId
            lastCommand: s(controlStateObj.last_command)
            lastResult: s(controlStateObj.last_command_result)
            lastError: s(controlStateObj.last_command_error)
        }

            Item {
                width: 1
                height: 16
            }
        }
    }
}

// Page Feedback
