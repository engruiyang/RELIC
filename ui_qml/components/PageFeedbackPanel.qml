import QtQuick
import QtQuick.Controls
GroupBox {
    title: "Page Feedback"
    property string pageId: ""
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""
    property string lastCommand: ""
    property string lastResult: ""
    property string lastError: ""
    Column {
        spacing: 2
        Label { text: "page_id: " + pageId }
        Label { text: "selected command_id: " + selectedCommandId }
        Label { text: "selected status: " + selectedStatus }
        Label { text: "execution_mode: " + selectedExecutionMode }
        Label { text: "native_action_id: " + selectedNativeActionId }
        Label { text: "last_command: " + lastCommand }
        Label { text: "last_command_result: " + lastResult }
        Label { text: "last_command_error: " + lastError }
    }
}
