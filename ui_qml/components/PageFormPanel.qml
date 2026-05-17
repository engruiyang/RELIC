import QtQuick
import QtQuick.Controls

GroupBox {
    title: "User Form"
    property string userId: ""
    property string displayName: ""
    signal createUser(string userId, string displayName)
    signal loadUser(string userId)

    Column {
        anchors.fill: parent
        spacing: 4
        TextField { placeholderText: "user_id"; text: parent.parent.userId; onTextChanged: parent.parent.userId = text }
        TextField { placeholderText: "display_name"; text: parent.parent.displayName; onTextChanged: parent.parent.displayName = text }
        Row {
            Button { text: "Create"; onClicked: parent.parent.parent.createUser(parent.parent.parent.userId, parent.parent.parent.displayName) }
            Button { text: "Load"; onClicked: parent.parent.parent.loadUser(parent.parent.parent.userId) }
        }
    }
}
