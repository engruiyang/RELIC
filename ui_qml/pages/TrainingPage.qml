import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    objectName: "TrainingPage"
    property var debugVisibleTokens: ["training", "trainingSessionPanel", "trainingRuntimePanel", "trainingHudPanel", "trainingGameCanvasPlaceholder", "trainingResultPanel"]
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property var gameHudObj: ({})
    property string commandSummary: ""
    property var actionResultObj: ({})
    signal invokeNative(string actionId)

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader { titleText: "Training Page"; subtitleText: "Session and runtime observability" }

        GroupBox {
            objectName: "trainingSessionPanel"
            title: "Session Actions"
            width: parent.width
            Row {
                spacing: 6
                Button { text: "Start Session"; onClicked: invokeNative("session.start") }
                Button { text: "Stop Session"; onClicked: invokeNative("session.stop") }
                Button { text: "Game Status"; onClicked: invokeNative("game.status") }
            }
        }

        GroupBox {
            objectName: "trainingRuntimePanel"
            title: "Runtime"
            width: parent.width
            Column {
                Label { text: "session_active: " + s(controlStateObj.session_active) }
                Label { text: "quality_state: " + s(runtimeObj.quality_state) }
            }
        }

        GroupBox {
            objectName: "trainingHudPanel"
            title: "Game HUD"
            width: parent.width
            Column {
                Label { text: "score: " + s(gameHudObj.score) }
                Label { text: "level: " + s(gameHudObj.level) }
            }
        }

        GroupBox {
            objectName: "trainingGameCanvasPlaceholder"
            title: "Canvas Placeholder"
            width: parent.width
            Label { text: "GameCanvas will be restored in TASK24" }
        }

        GroupBox {
            title: "Training List"
            width: parent.width
            PageListPanel { width: parent.width; height: 90; items: (actionResultObj.items || []) }
        }



        GroupBox {
            title: "Training Detail"
            width: parent.width
            PageDetailPanel { width: parent.width; height: 90; detailObj: (actionResultObj.detail || {}) }
        }

        GroupBox {
            objectName: "trainingResultPanel"
            title: "Training Action Result"
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
