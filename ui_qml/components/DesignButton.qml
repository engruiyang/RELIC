import QtQuick
import QtQuick.Controls

Item {
    id: root

    property string text: ""
    property var buttonStyleObj: ({})
    property var themeObj: ({})
    signal clicked()

    implicitWidth: Math.max(128, label.implicitWidth + 28)
    implicitHeight: Math.max(34, label.implicitHeight + 16)
    width: implicitWidth
    height: implicitHeight

    readonly property bool pressed: mouseArea.pressed
    readonly property bool hovered: mouseArea.containsMouse
    readonly property var colorsObj: themeObj.colors || ({})
    readonly property var normalObj: buttonStyleObj.normal || ({})
    readonly property var pressedObj: buttonStyleObj.pressed || ({})
    readonly property var disabledObj: buttonStyleObj.disabled || ({})

    function styleValue(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    Rectangle {
        anchors.fill: parent
        radius: Number(root.styleValue(root.buttonStyleObj, "radius", 8))
        color: !root.enabled
               ? root.styleValue(root.disabledObj, "background", "#CBD5E1")
               : (root.pressed
                  ? root.styleValue(root.pressedObj, "background", "#1D4ED8")
                  : root.styleValue(root.normalObj, "background", root.styleValue(root.colorsObj, "accent", "#2563EB")))
        border.width: 1
        border.color: !root.enabled
                      ? root.styleValue(root.disabledObj, "border", "#94A3B8")
                      : (root.pressed
                         ? root.styleValue(root.pressedObj, "border", "#1E40AF")
                         : root.styleValue(root.normalObj, "border", "#1D4ED8"))
        opacity: root.enabled ? 1.0 : 0.65
    }

    Text {
        id: label
        anchors.centerIn: parent
        text: root.text
        color: !root.enabled
               ? root.styleValue(root.disabledObj, "text", "#64748B")
               : (root.pressed
                  ? root.styleValue(root.pressedObj, "text", "#FFFFFF")
                  : root.styleValue(root.normalObj, "text", "#FFFFFF"))
        font.pixelSize: Number(((root.themeObj.typography || ({})).body_size) || 14)
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        enabled: root.enabled
        onClicked: root.clicked()
    }

    // TASK25B DesignButton is self-drawn with MouseArea; it avoids native Button background customization.
}
