import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    objectName: "ReportPage"
    property var debugVisibleTokens: ["report", "reportLatestPanel", "reportListPanel", "reportDetailPanel", "reportResultPanel"]
    property var controlStateObj: ({})
    property var sessionObj: ({})
    property string commandSummary: ""
    property var actionResultObj: ({})
    signal invokeNative(string actionId)

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader { titleText: "Report Page"; subtitleText: "Training output and report workflow" }

        GroupBox {
            objectName: "reportLatestPanel"
            title: "Latest Report"
            width: parent.width
            Row {
                Button { text: "Refresh"; onClicked: invokeNative("report.refresh") }
                Button { text: "Export"; onClicked: invokeNative("report.export") }
                Label { text: "latest_report_path: " + s(controlStateObj.latest_report_path) }
            }
        }

        GroupBox {
            objectName: "reportListPanel"
            title: "Report List"
            width: parent.width
            Column {
                Row {
                    Button { text: "List Sessions"; onClicked: invokeNative("report.list") }
                    Button { text: "Show Session"; onClicked: invokeNative("report.show") }
                }
                PageListPanel { width: parent.width; height: 90; items: (actionResultObj.items || []) }
            }
        }

        GroupBox {
            objectName: "reportDetailPanel"
            title: "Report Detail"
            width: parent.width
            PageDetailPanel { width: parent.width; height: 90; detailObj: (actionResultObj.detail || {}) }
        }

        GroupBox {
            objectName: "reportResultPanel"
            title: "Report Action Result"
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
