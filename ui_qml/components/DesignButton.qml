import QtQuick

Rectangle {
    id: root

    property string text: "Button"
    property bool enabled: true
    property var buttonStyleObj: ({})
    property var themeObj: ({})
    signal clicked()

    function value(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function stateStyle() {
        if (!root.enabled) {
            return buttonStyleObj.disabled || ({})
        }
        if (mouseArea.pressed) {
            return buttonStyleObj.pressed || ({})
        }
        if (mouseArea.containsMouse) {
            return buttonStyleObj.hover || buttonStyleObj.normal || ({})
        }
        return buttonStyleObj.normal || ({})
    }

    implicitWidth: Math.max(92, label.implicitWidth + Number(value(buttonStyleObj, "padding_x", 14)) * 2)
    implicitHeight: Math.max(32, label.implicitHeight + Number(value(buttonStyleObj, "padding_y", 10)))
    radius: Number(value(buttonStyleObj, "radius", 8))
    color: value(stateStyle(), "background", root.enabled ? "#2563EB" : "#6B7280")
    border.width: Number(value(buttonStyleObj, "border_width", 1))
    border.color: value(stateStyle(), "border", "#1D4ED8")
    opacity: root.enabled ? 1.0 : 0.65

    Text {
        id: label
        anchors.centerIn: parent
        text: root.text
        color: root.value(root.stateStyle(), "text", "#FFFFFF")
        font.family: root.value(root.themeObj.typography || ({}), "font_family", "Sans Serif")
        font.pixelSize: Number(root.value(root.themeObj.typography || ({}), "body_size", 14))
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

    // TASK25B DesignButton is self-painted; no native Button background customization is used.
}
