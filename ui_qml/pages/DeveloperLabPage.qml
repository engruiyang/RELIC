import QtQuick
import QtQuick.Controls
import "../components"

Item {
    property var controlStateObj: ({})
    property string commandSummary: ""
    property var actionResultObj: ({})
    signal invokeNative(string actionId)
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

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader {
            titleText: "Developer Lab"
            subtitleText: "Advanced/manual/copy_only command catalog"
        }

        GroupBox {
            title: "Developer Lab Actions"
            Column {
                Button { text: "Run devlab.run"; onClicked: { selectedCliReference = "manual_or_copy_only"; invokeNative("devlab.run") } }
                Button { text: "Copy Command"; onClicked: invokeNative("devlab.copy_command") }
                Button { text: "Copy Payload"; onClicked: invokeNative("devlab.copy_payload") }
                
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

        GroupBox {
            title: "Dynamic Content"
            Column {
                PageListPanel { width: parent.width; height: 80; items: (actionResultObj.items || []) }
                PageDetailPanel { width: parent.width; height: 80; detailObj: ({action_id: actionResultObj.action_id, page_id: actionResultObj.page_id, status: actionResultObj.status, payload: actionResultObj.payload}) }
                PageResultPanel { width: parent.width; actionResult: (actionResultObj || {"status":"n/a"}) }
            }
        }

        PageFeedbackPanel {
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
