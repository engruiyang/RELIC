import QtQuick
import QtQuick.Controls
GroupBox {
    title: "Page Feedback"
    property string pageId: ""
    property var selectedCommandId: ""
    property var selectedStatus: ""
    property var selectedExecutionMode: ""
    property var selectedNativeActionId: ""
    property var lastCommand: ""
    property var lastResult: ""
    property var lastError: ""
    Column {
        spacing: 2
        Label { text: "page_id: " + pageId }
        Label { text: "selected command_id: " + String(selectedCommandId === undefined || selectedCommandId === null ? "n/a" : selectedCommandId) }
        Label { text: "selected status: " + String(selectedStatus === undefined || selectedStatus === null ? "n/a" : selectedStatus) }
        Label { text: "execution_mode: " + String(selectedExecutionMode === undefined || selectedExecutionMode === null ? "n/a" : selectedExecutionMode) }
        Label { text: "native_action_id: " + String(selectedNativeActionId === undefined || selectedNativeActionId === null ? "n/a" : selectedNativeActionId) }
        Label { text: "last_command: " + String(lastCommand === undefined || lastCommand === null ? "n/a" : lastCommand) }
        Label { text: "last_command_result: " + String(lastResult === undefined || lastResult === null ? "n/a" : lastResult) }
        Label { text: "last_command_error: " + String(lastError === undefined || lastError === null ? "n/a" : lastError) }
    }
}
