import QtQuick
import QtQuick.Controls
import "../components"

Item {
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property var gameHudObj: ({})
    property string commandSummary: ""
    property var actionResultObj: ({})
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""

    signal invokeNative(string actionId)

    function pick(id, status, mode, nativeActionId) {
        selectedCommandId = id
        selectedStatus = status
        selectedExecutionMode = mode
        selectedNativeActionId = nativeActionId
        if (mode === "native" && nativeActionId !== "") {
            invokeNative(nativeActionId)
        }
    }

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader {
            titleText: "Training Page"
            subtitleText: "Training/game actions only"
        }

        GroupBox {
            title: "Training Page Actions"
            Row {
                spacing: 4
                Button {
                    text: "Select Game"
                    enabled: false
                }
                Button {
                    text: "Start Session"
                    onClicked: pick("training.start_session", "native_ready", "native", "session.start")
                }
                Button {
                    text: "Stop Session"
                    onClicked: pick("training.stop_session", "native_ready", "native", "session.stop")
                }
                Button {
                    text: "Safe Stop"
                    onClicked: pick("live.safe_stop", "native_ready", "native", "live.safe_stop")
                }
                Button {
                    text: "Session Status"
                    onClicked: pick("training.session_status", "native_ready", "native", "session.status")
                }
                Button {
                    text: "Game Status"
                    onClicked: pick("game.status", "native_ready", "native", "game.status")
                }
            }
        }

        GroupBox {
            title: "Training State"
            Column {
                Label { text: "selected_game_id: " + s(controlStateObj.current_game_id) }
                Label { text: "session_active: " + s(controlStateObj.session_active) }
                Label { text: "current_session_id: " + s(controlStateObj.current_session_id) }
                Label { text: "session_elapsed_ms: " + s(controlStateObj.session_elapsed_ms) }
                Label { text: "quality_state: " + s(runtimeObj.quality_state) }
                Label { text: "control_state: " + s(runtimeObj.control_state) }
                Label { text: "fi_smoothed: " + s(runtimeObj.fi_smoothed) }
                Label { text: "attention_fresh: " + s(runtimeObj.attention_fresh) }
                Label { text: "gyro_fresh: " + s(runtimeObj.gyro_fresh) }
                Label { text: "score: " + s(gameHudObj.score) }
                Label { text: "combo: " + s(gameHudObj.combo) }
                Label { text: "level: " + s(gameHudObj.level) }
                Label { text: "behavior_sample_count: " + s(controlStateObj.behavior_sample_count) }
                Label { text: "score_update_count: " + s(gameHudObj.score_update_count) }
                Label { text: "feedback_hint: " + s(gameHudObj.feedback_hint) }
            }
        }

        Label { text: "GameCanvas will be restored in TASK24" }
        Label { text: "Fragment Lock / 碎片锁定: reference ready" }
        Label { text: "Signal Hunter / 信号猎手: planned" }
        Label { text: "Stabilizer / 稳定协议: planned" }

        GroupBox {
            title: "Page Commands"
            Label {
                text: commandSummary
                wrapMode: Text.WordWrap
            }
        }

        GroupBox {
            title: "Dynamic Content"
            Column {
                PageListPanel { width: parent.width; height: 80; items: (controlStateObj.items || []) }
                PageDetailPanel { width: parent.width; height: 80; detailObj: (controlStateObj || {}) }
                PageResultPanel { width: parent.width; actionResult: (actionResultObj || {"status":"n/a"}) }
            }
        }

        PageFeedbackPanel {
            pageId: "training"
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
