import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    objectName: "HomePage"
    property var debugVisibleTokens: ["home", "workflow", "homeSummaryPanel", "homeWorkflowPanel", "homeResultPanel"]
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property string commandSummary: ""
    signal navigateTo(string pageId)
    signal invokeNative(string actionId)

    function s(v) { return (v === undefined || v === null || v === "") ? "n/a" : String(v) }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader { titleText: "Home"; subtitleText: "Workflow entry: Home -> User/Profile -> Calibration -> Training -> Report" }

        GroupBox {
            objectName: "homeSummaryPanel"
            title: "Home Summary"
            width: parent.width
            Column {
                Label { text: "current_user_id: " + s(controlStateObj.current_user_id) }
                Label { text: "profile_status: " + s(controlStateObj.profile_status) }
                Label { text: "calibration_status: " + s(controlStateObj.calibration_status) }
                Label { text: "session_active: " + s(controlStateObj.session_active) }
                Label { text: "connection_status: " + s(runtimeObj.connection_status) }
            }
        }

        GroupBox {
            objectName: "homeWorkflowPanel"
            title: "Workflow Shortcuts"
            width: parent.width
            Row {
                spacing: 6
                Button { text: "Go User"; onClicked: navigateTo("user") }
                Button { text: "Go Calibration"; onClicked: navigateTo("calibration") }
                Button { text: "Go Training"; onClicked: navigateTo("training") }
                Button { text: "Go Report"; onClicked: navigateTo("report") }
                Button { text: "Refresh"; onClicked: invokeNative("app.refresh_now") }
            }
        }

        GroupBox {
            objectName: "homeResultPanel"
            title: "Home Empty State"
            width: parent.width
            Label { text: "No list content on Home. Use User/Calibration/Report pages for action-driven lists." }
        }

        GroupBox {
            title: "Page Commands"
            width: parent.width
            Label { text: commandSummary; wrapMode: Text.WordWrap }
        }

        // Page Feedback
    }
}
