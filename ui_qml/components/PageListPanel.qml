import QtQuick
import QtQuick.Controls

GroupBox {
    title: "Items"
    property var items: ([])
    property string emptyMessage: "No items"
    TextArea {
        anchors.fill: parent
        readOnly: true
        wrapMode: Text.WrapAnywhere
        text: (items && items.length) ? JSON.stringify(items, null, 2) : emptyMessage
    }
}
