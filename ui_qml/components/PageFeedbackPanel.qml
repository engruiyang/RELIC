import QtQuick

Rectangle {
    id: feedbackPanel

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

    readonly property var colorsObj: designThemeObj.colors || ({})
    readonly property color textColor: colorsObj.text || "#0F172A"
    readonly property color mutedTextColor: colorsObj.text_muted || "#475569"
    readonly property var effectiveStyleObj: Object.keys(feedbackStyleObj || ({})).length > 0 ? feedbackStyleObj : ((componentStyleObj || ({})).feedback_panel || ({}))

    implicitWidth: 360
    implicitHeight: feedbackColumn.implicitHeight + 20
    color: effectiveStyleObj.background || colorsObj.panel || "#FFFFFF"
    border.color: effectiveStyleObj.border || colorsObj.panel_border || "#CBD5E1"
    border.width: Number(effectiveStyleObj.border_width || 1)
    radius: Number(effectiveStyleObj.radius || 8)
    opacity: Number(effectiveStyleObj.opacity === undefined ? 0.96 : effectiveStyleObj.opacity)

    Column {
        id: feedbackColumn
        anchors.fill: parent
        anchors.margins: Number(feedbackPanel.effectiveStyleObj.padding || 10)
        spacing: Number(feedbackPanel.effectiveStyleObj.spacing || 2)

        Text {
            text: "Page Feedback"
            color: feedbackPanel.textColor
            font.bold: true
            font.pixelSize: Number((feedbackPanel.designThemeObj.typography || ({})).subtitle_size || 14)
        }
        Text { text: "page_id: " + feedbackPanel.pageId; color: feedbackPanel.mutedTextColor }
        Text { text: "selected command_id: " + String(feedbackPanel.selectedCommandId === undefined || feedbackPanel.selectedCommandId === null ? "n/a" : feedbackPanel.selectedCommandId); color: feedbackPanel.textColor }
        Text { text: "selected status: " + String(feedbackPanel.selectedStatus === undefined || feedbackPanel.selectedStatus === null ? "n/a" : feedbackPanel.selectedStatus); color: feedbackPanel.textColor }
        Text { text: "execution_mode: " + String(feedbackPanel.selectedExecutionMode === undefined || feedbackPanel.selectedExecutionMode === null ? "n/a" : feedbackPanel.selectedExecutionMode); color: feedbackPanel.textColor }
        Text { text: "native_action_id: " + String(feedbackPanel.selectedNativeActionId === undefined || feedbackPanel.selectedNativeActionId === null ? "n/a" : feedbackPanel.selectedNativeActionId); color: feedbackPanel.textColor }
        Text { text: "last_command: " + String(feedbackPanel.lastCommand === undefined || feedbackPanel.lastCommand === null ? "n/a" : feedbackPanel.lastCommand); color: feedbackPanel.textColor }
        Text { text: "last_command_result: " + String(feedbackPanel.lastResult === undefined || feedbackPanel.lastResult === null ? "n/a" : feedbackPanel.lastResult); color: feedbackPanel.textColor }
        Text { text: "last_command_error: " + String(feedbackPanel.lastError === undefined || feedbackPanel.lastError === null ? "n/a" : feedbackPanel.lastError); color: feedbackPanel.textColor }
    }

    // TASK25B-2H PageFeedbackPanel is self-painted; no native Control background customization.
}
