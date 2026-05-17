import QtQuick
import QtQuick.Controls

GroupBox {
    title: "Detail"
    property var detailObj: ({})
    TextArea {
        anchors.fill: parent
        readOnly: true
        wrapMode: Text.WrapAnywhere
        text: JSON.stringify(detailObj || {}, null, 2)
    }
}
