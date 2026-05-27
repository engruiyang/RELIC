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
                slot1CardId: "runtime_io_card"
                slot2CardId: "quick_actions_card"
                slot3CardId: "recent_session_card"
                slot4CardId: "relic_identity_card"
                slot1CardType: "runtime"
                slot2CardType: "actions"
                slot3CardType: "session"
                slot4CardType: "identity"
                slot1Title: "Runtime I/O"
                slot2Title: "Quick Actions"
                slot3Title: "Recent Session"
                slot4Title: "RELIC Identity"
                slot1Subtitle: "Connection and stream health"
                slot2Subtitle: "Safety and refresh"
                slot3Subtitle: "Session summary"
                slot4Subtitle: "Brand and visual"
                slot1Required: true
                slot2Required: true
                slot3Required: false
                slot4Required: false
                slot1Locked: true
                slot2Locked: true
                slot3Locked: false
                slot4Locked: false
                slot1RectText: "x=10.0, y=10.0, w=386.0, h=290.0"
                slot2RectText: "x=404.0, y=10.0, w=386.0, h=290.0"
                slot3RectText: "x=10.0, y=308.0, w=584.0, h=290.0"
                slot4RectText: "x=798.0, y=10.0, w=386.0, h=588.0"
                slot1WidgetCount: 3
                slot2WidgetCount: 2
                slot3WidgetCount: 3
                slot4WidgetCount: 2
                slot1ActionIdsText: "n/a"
                slot2ActionIdsText: "app.refresh_now, live.safe_stop"
                slot3ActionIdsText: "n/a"
                slot4ActionIdsText: "n/a"
                slot1SourceRootsText: "runtimeSnapshot"
                slot2SourceRootsText: "n/a"
                slot3SourceRootsText: "gameHudJson, sessionState"
                slot4SourceRootsText: "renderResourcesJson"
                slot1FirstWidgetLabelsText: "Runtime, Stream, Attention"
                slot2FirstWidgetLabelsText: "Refresh, Safe Stop"
                slot3FirstWidgetLabelsText: "Active, Session ID, HUD"
                slot4FirstWidgetLabelsText: "Identity, Tagline"
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
