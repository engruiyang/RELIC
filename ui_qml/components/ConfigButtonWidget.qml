import QtQuick 2.15

Item {
    id: root

    property var guiBridge: null

    property string label: "Action"
    property string actionId: ""
    property string argsJson: "{}"
    property string variant: "primary"

    property bool enabledValue: true
    property bool confirmEnabled: false
    property string confirmMessage: "Confirm?"
    property bool required: false

    property int buttonWidth: 148
    property int buttonHeight: 40
    property int radiusValue: 12

    property color primaryColor: "#2D6CDF"
    property color secondaryColor: "#273244"
    property color dangerColor: "#B63A3A"
    property color disabledColor: "#3A3F48"
    property color borderColor: "#4A5C76"
    property color textColor: "#FFFFFF"

    property bool confirmArmed: false

    signal actionRequested(string actionId, string argsJson)

    width: buttonWidth
    height: buttonHeight
    opacity: enabledValue ? 1.0 : 0.48

    Rectangle {
        id: buttonBody
        anchors.fill: parent
        radius: root.radiusValue
        color: !root.enabledValue ? root.disabledColor
            : root.variant === "danger" ? root.dangerColor
            : root.variant === "secondary" ? root.secondaryColor
            : root.primaryColor
        border.color: root.confirmArmed ? "#FFD479" : root.borderColor
        border.width: root.required ? 2 : 1
    }

    Text {
        anchors.centerIn: parent
        text: root.confirmArmed ? root.confirmMessage : root.label
        color: root.textColor
        font.pixelSize: 13
        font.bold: root.required
        elide: Text.ElideRight
        width: parent.width - 16
        horizontalAlignment: Text.AlignHCenter
    }

    MouseArea {
        anchors.fill: parent
        enabled: root.enabledValue
        onClicked: {
            if (root.actionId.length === 0) {
                return
            }

            if (root.confirmEnabled && !root.confirmArmed) {
                root.confirmArmed = true
                return
            }

            root.actionRequested(root.actionId, root.argsJson)

            if (root.guiBridge) {
                root.guiBridge.invokeAction(root.actionId, root.argsJson)
            }

            root.confirmArmed = false
        }
    }
}
