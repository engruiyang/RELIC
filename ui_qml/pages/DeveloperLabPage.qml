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

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: (root.designThemeObj.colors && root.designThemeObj.colors.background) ? root.designThemeObj.colors.background : "#F8FAFC"
    }

    Column {
        anchors.fill: parent
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
            selectedCommandId: parent.selectedCommandId
            selectedStatus: parent.selectedStatus
            selectedExecutionMode: parent.selectedExecutionMode
            selectedNativeActionId: parent.selectedNativeActionId
            lastCommand: s(controlStateObj.last_command)
            lastResult: s(controlStateObj.last_command_result)
            lastError: s(controlStateObj.last_command_error)
        }
    }
}

// Page Feedback
