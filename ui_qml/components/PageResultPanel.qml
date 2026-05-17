import QtQuick
import QtQuick.Controls

GroupBox {
    title: "Action Result"
    property var actionResult: ({})

    function s(v) { return (v === undefined || v === null || v === "") ? "n/a" : String(v) }

    Column {
        anchors.fill: parent
        spacing: 4
        Label { text: "action_id: " + s(actionResult.action_id) }
        Label { text: "status: " + s(actionResult.status) }
        Label { text: "message: " + s(actionResult.message) }
        Label { text: "summary: " + s(actionResult.summary) }
        Label { text: "error: " + s(actionResult.error) }
        TextArea { readOnly: true; wrapMode: Text.WrapAnywhere; text: JSON.stringify(actionResult.detail || {}, null, 2); implicitHeight: 90 }
    }
}
