import QtQuick
import QtQuick.Controls
import "../components"

Item {
    property var controlStateObj: ({})
    property var sessionObj: ({})
    property string commandSummary: ""
    property var actionResultObj: ({})
    signal invokeNative(string actionId)
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""

    function pick(id, status, mode, nativeActionId) {
        selectedCommandId = id
        selectedStatus = status
        selectedExecutionMode = mode
        selectedNativeActionId = nativeActionId
        if (mode === "native" && nativeActionId !== "") { invokeNative(nativeActionId) }
    }

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader {
            titleText: "Report Page"
            subtitleText: "Report/session summary"
        }

        GroupBox {
            title: "Report Page Actions"
            Row {
                spacing: 4
                Button {
                    text: "List Sessions"
                    onClicked: pick("report.list", "native_ready", "native", "report.list")
                }
                Button {
                    text: "Show Session"
                    onClicked: pick("report.show", "native_ready", "native", "report.show")
                }
                Button {
                    text: "Latest Report"
                    onClicked: pick("report.refresh", "native_ready", "native", "report.refresh")
                }
                Button {
                    text: "Replay Summary"
                    enabled: false
                }
                Button {
                    text: "Open Path Manual"
                    onClicked: pick("report.export", "native_ready", "native", "report.export")
                }
            }
        }

        GroupBox {
            title: "Report State"
            Column {
                Label { text: "latest_report_path: " + s(controlStateObj.latest_report_path) }
                Label { text: "last_session_status: " + s(controlStateObj.last_session_status) }
                Label { text: "current_session_id: " + s(controlStateObj.current_session_id) }
                Label { text: "session_active: " + s(controlStateObj.session_active) }
                Label { text: "report_status: " + s(controlStateObj.report_status) }
                Label { text: "log_path: " + s(controlStateObj.log_path) }
                Label { text: "game_event_count: " + s(controlStateObj.game_event_count) }
                Label { text: "behavior_sample_count: " + s(sessionObj.behavior_sample_count) }
            }
        }

        Label {
            text: "Full report viewer will be handled in later tasks."
        }

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
                PageListPanel { width: parent.width; height: 80; items: (actionResultObj.items || []) }
                PageDetailPanel { width: parent.width; height: 80; detailObj: (actionResultObj.detail || {}) }
                PageResultPanel { width: parent.width; actionResult: (actionResultObj || {"status":"n/a"}) }
            }
        }

        PageFeedbackPanel {
            pageId: "report"
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
