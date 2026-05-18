import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    objectName: "DiagnosticsPage"
    property var debugVisibleTokens: ["diagnostics", "diagnosticsLiveBusPanel", "diagnosticsQualityPanel", "diagnosticsSnapshotPanel"]
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property string commandSummary: ""
    signal invokeNative(string actionId)

    function s(v) { return (v === undefined || v === null || v === "") ? "n/a" : String(v) }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader { titleText: "Developer Diagnostics Console"; subtitleText: "Live Input / Quality / Focus" }
        Label { text: "Live Input" }
        Label { text: "Quality / Focus" }

        GroupBox {
            objectName: "diagnosticsLiveBusPanel"
            title: "Live Bus"
            width: parent.width
            Label { text: "connection_status: " + s(runtimeObj.connection_status) }
        }

        GroupBox {
            objectName: "diagnosticsQualityPanel"
            title: "Quality"
            width: parent.width
            Label { text: "quality_state: " + s(runtimeObj.quality_state) }
            Label { text: "warning_flags: " + s(runtimeObj.warning_flags) }
            Label { text: "error_flags: " + s(runtimeObj.error_flags) }
        }

        GroupBox {
            objectName: "diagnosticsSnapshotPanel"
            title: "Snapshot"
            width: parent.width
            Label { text: "session_id: " + s(sessionObj.session_id) }
        }

        GroupBox {
            title: "Diagnostics List"
            width: parent.width
            PageListPanel { width: parent.width; height: 90; items: [] }
        }

        GroupBox {
            title: "Diagnostics Detail"
            width: parent.width
            PageDetailPanel { width: parent.width; height: 90; detailObj: ({"warning_flags": runtimeObj.warning_flags, "error_flags": runtimeObj.error_flags}) }
        }

        GroupBox {
            title: "Diagnostics Result"
            width: parent.width
            PageResultPanel { width: parent.width; actionResult: ({"status": "n/a"}) }
        }

        GroupBox {
            title: "Page Commands"
            Label { text: commandSummary; wrapMode: Text.WordWrap }
        }

        // Page Feedback
    }
}
