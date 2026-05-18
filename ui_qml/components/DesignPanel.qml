import QtQuick

Rectangle {
    id: root

    property var panelStyleObj: ({})
    property var themeObj: ({})
    property int panelPadding: Number(value(panelStyleObj, "padding", 12))
    default property alias contentData: contentItem.data

    function value(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function themeColor(key, fallbackValue) {
        var colors = themeObj.colors || ({})
        return value(colors, key, fallbackValue)
    }

    color: value(panelStyleObj, "background", themeColor("panel", "#172330"))
    opacity: Number(value(panelStyleObj, "opacity", 1.0))
    radius: Number(value(panelStyleObj, "radius", 8))
    border.width: Number(value(panelStyleObj, "border_width", 1))
    border.color: value(panelStyleObj, "border", themeColor("panel_border", "#374151"))
    clip: true

    Item {
        id: contentItem
        anchors.fill: parent
        anchors.margins: root.panelPadding
    }

    // TASK25B DesignPanel consumes component.panel background/border/radius/padding/opacity tokens.
}
