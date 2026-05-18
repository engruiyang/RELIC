import QtQuick
import QtQuick.Controls
import "../components"
Item {
    id: root
    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var renderResourcesObj: ({})
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property string commandSummary: ""
    signal navigateTo(string pageId)
    signal invokeNative(string actionId)
    width: parent ? parent.width : 900
    height: parent ? parent.height : 600
    function safeText(v){ return (v===undefined||v===null||v==="")?"n/a":String(v) }
    function nextAction(){ if (safeText(controlStateObj.current_user_id)==="n/a") return "Next Action: Go User"; if (safeText(controlStateObj.calibration_usable)!=="true") return "Next Action: Go Calibration"; return "Next Action: Go Training" }
    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: (root.designThemeObj.colors && root.designThemeObj.colors.background) ? root.designThemeObj.colors.background : "#F8FAFC"
    }

    Column { anchors.fill: parent; spacing: 6
        PageHeader {
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            headerStyleObj: root.componentStyleObj.header || ({}) titleText: "Home"; subtitleText: "Professional overview page" }
        GroupBox { title: "State Summary"; Column {
            Label { text: "current_user_id: " + safeText(controlStateObj.current_user_id) }
            Label { text: "profile_status: " + safeText(controlStateObj.profile_status) }
            Label { text: "calibration_status: " + safeText(controlStateObj.calibration_status) }
            Label { text: "calibration_usable: " + safeText(controlStateObj.calibration_usable) }
            Label { text: "connection_status: " + safeText(runtimeObj.connection_status) }
            Label { text: "quality_state: " + safeText(runtimeObj.quality_state) }
            Label { text: "control_state: " + safeText(runtimeObj.control_state) }
            Label { text: "session_active: " + safeText(controlStateObj.session_active) }
            Label { text: "latest_report_path: " + safeText(controlStateObj.latest_report_path) }
            Label { text: nextAction() }
        }}
        GroupBox { title: "Action Panel"; Row { spacing: 4
            Button { text: "Go User"; onClicked: navigateTo("user") }
            Button { text: "Go Calibration"; onClicked: navigateTo("calibration") }
            Button { text: "Go Training"; onClicked: navigateTo("training") }
            Button { text: "Go Report"; onClicked: navigateTo("report") }
            Button { text: "Go Diagnostics"; onClicked: navigateTo("diagnostics") }
            Button { text: "Refresh"; onClicked: invokeNative("app.refresh_now") }
        }}
        GroupBox { title: "Page Commands"; Label { text: commandSummary; wrapMode: Text.WordWrap } }
        PageFeedbackPanel {
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            feedbackStyleObj: root.componentStyleObj.feedback_panel || ({}) pageId: "home"; lastCommand: safeText(controlStateObj.last_command); lastResult: safeText(controlStateObj.last_command_result); lastError: safeText(controlStateObj.last_command_error) }
    }
}

// Page Feedback
