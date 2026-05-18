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
    property var designThemeObj: ({})
    property var componentStyleObj: ({})
    property var feedbackStyleObj: ({})

    readonly property color textColor: (designThemeObj.colors && designThemeObj.colors.text) ? designThemeObj.colors.text : "#0F172A"

    background: Rectangle {
        color: feedbackStyleObj.background || "#FFFFFF"
        border.color: feedbackStyleObj.border || "#CBD5E1"
        border.width: 1
        radius: feedbackStyleObj.radius !== undefined ? Number(feedbackStyleObj.radius) : 8
        opacity: feedbackStyleObj.opacity !== undefined ? Number(feedbackStyleObj.opacity) : 0.96
    }

    Column {
        spacing: 2
        Label { text: "page_id: " + pageId; color: textColor }
        Label { text: "selected command_id: " + String(selectedCommandId === undefined || selectedCommandId === null ? "n/a" : selectedCommandId); color: textColor }
        Label { text: "selected status: " + String(selectedStatus === undefined || selectedStatus === null ? "n/a" : selectedStatus); color: textColor }
        Label { text: "execution_mode: " + String(selectedExecutionMode === undefined || selectedExecutionMode === null ? "n/a" : selectedExecutionMode); color: textColor }
        Label { text: "native_action_id: " + String(selectedNativeActionId === undefined || selectedNativeActionId === null ? "n/a" : selectedNativeActionId); color: textColor }
        Label { text: "last_command: " + String(lastCommand === undefined || lastCommand === null ? "n/a" : lastCommand); color: textColor }
        Label { text: "last_command_result: " + String(lastResult === undefined || lastResult === null ? "n/a" : lastResult); color: textColor }
        Label { text: "last_command_error: " + String(lastError === undefined || lastError === null ? "n/a" : lastError); color: textColor }
    }
}
