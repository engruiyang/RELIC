import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    objectName: "CalibrationPage"
    property var debugVisibleTokens: [
        "calibration",
        "calibrationUserGatePanel",
        "calibrationBindingPanel",
        "calibrationLatestPanel",
        "calibrationListPanel",
        "calibrationDetailPanel",
        "calibrationResultPanel"
    ]
    property var controlStateObj: ({})
    property string commandSummary: ""
    property var actionResultObj: ({})
    signal invokeNative(string actionId)

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    function hasUser() {
        return s(controlStateObj.current_user_id) !== "n/a"
    }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader {
            titleText: "Calibration Page"
            subtitleText: "Calibration requires a current user"
        }

        GroupBox {
            objectName: "calibrationUserGatePanel"
            title: "User Gate"
            width: parent.width
            Column {
                Label { text: hasUser() ? "current_user_id ready" : "No current user. Go to User page first." }
                Label { text: "Main flow: User/Profile -> Calibration -> Training" }
            }
        }

        GroupBox {
            objectName: "calibrationBindingPanel"
            title: "Calibration Actions"
            visible: hasUser()
            width: parent.width
            Row {
                spacing: 6
                Button { text: "Calibration Status"; onClicked: invokeNative("calibration.status") }
                Button { text: "List Calibrations"; onClicked: invokeNative("calibration.list") }
                Button { text: "Latest Calibration"; onClicked: invokeNative("calibration.latest") }
                Button { text: "Show Calibration"; onClicked: invokeNative("calibration.show") }
                Button { text: "Bind Calibration"; onClicked: invokeNative("calibration.bind") }
                Button { text: "Start Calibration"; onClicked: invokeNative("calibration.start") }
            }
        }

        GroupBox {
            objectName: "calibrationLatestPanel"
            title: "Latest Calibration"
            visible: hasUser()
            width: parent.width
            PageDetailPanel { width: parent.width; height: 80; detailObj: (actionResultObj.detail || {}) }
        }

        GroupBox {
            objectName: "calibrationListPanel"
            title: "Calibration List"
            visible: hasUser()
            width: parent.width
            PageListPanel { width: parent.width; height: 90; items: (actionResultObj.items || []) }
        }

        GroupBox {
            objectName: "calibrationDetailPanel"
            title: "Calibration Detail"
            visible: hasUser()
            width: parent.width
            Label { text: "empty_state: select calibration from list to show details." }
        }

        GroupBox {
            objectName: "calibrationResultPanel"
            title: "Calibration Action Result"
            width: parent.width
            PageResultPanel { width: parent.width; actionResult: (actionResultObj || {"status": "n/a"}) }
        }

        GroupBox {
            title: "Page Commands"
            Label { text: commandSummary; wrapMode: Text.WordWrap }
        }

        // Page Feedback
    }
}
