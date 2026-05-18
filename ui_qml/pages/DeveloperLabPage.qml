import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    objectName: "DeveloperLabPage"
    property var debugVisibleTokens: ["developer_lab", "developerCommandDetailPanel", "developerPayloadPreviewPanel", "developerRunResultPanel", "developerMetadataPanel"]
    property var controlStateObj: ({})
    property string commandSummary: ""
    property var actionResultObj: ({})
    signal invokeNative(string actionId)

    function s(v) { return (v === undefined || v === null || v === "") ? "n/a" : String(v) }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader { titleText: "Developer Lab"; subtitleText: "Manual and advanced actions" }

        GroupBox {
            objectName: "developerCommandDetailPanel"
            title: "Command Detail"
            width: parent.width
            Button { text: "Run devlab.run"; onClicked: invokeNative("devlab.run") }
        }

        GroupBox {
            objectName: "developerPayloadPreviewPanel"
            title: "Payload Preview"
            width: parent.width
            PageDetailPanel { width: parent.width; height: 90; detailObj: (actionResultObj.payload || {}) }
        }

        GroupBox {
            title: "Developer List"
            width: parent.width
            PageListPanel { width: parent.width; height: 90; items: (actionResultObj.items || []) }
        }

        GroupBox {
            objectName: "developerRunResultPanel"
            title: "Run Result"
            width: parent.width
            PageResultPanel { width: parent.width; actionResult: (actionResultObj || {"status": "n/a"}) }
        }

        GroupBox {
            objectName: "developerMetadataPanel"
            title: "Metadata"
            width: parent.width
            Label { text: "last_command: " + s(controlStateObj.last_command) }
        }

        GroupBox {
            title: "Page Commands"
            Label { text: commandSummary; wrapMode: Text.WordWrap }
        }

        // Page Feedback
    }
}
