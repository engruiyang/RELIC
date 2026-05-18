import QtQuick

Rectangle {
    id: root

    property string label: "metric"
    property string value: "n/a"
    property var cardStyleObj: ({})
    property var themeObj: ({})

    function pick(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function colors() {
        return themeObj.colors || ({})
    }

    color: pick(cardStyleObj, "background", pick(colors(), "panel", "#0F172A"))
    radius: Number(pick(cardStyleObj, "radius", 10))
    border.width: Number(pick(cardStyleObj, "border_width", 1))
    border.color: pick(cardStyleObj, "border", pick(colors(), "panel_border", "#334155"))
    implicitWidth: Number(pick(cardStyleObj, "width", 160))
    implicitHeight: Number(pick(cardStyleObj, "height", 86))

    Column {
        anchors.fill: parent
        anchors.margins: Number(root.pick(cardStyleObj, "padding", 10))
        spacing: 4

        Text {
            width: parent.width
            text: root.label
            color: root.pick(cardStyleObj, "label_color", root.pick(root.colors(), "text_muted", "#94A3B8"))
            font.pixelSize: Number(root.pick(cardStyleObj, "label_size", 12))
            font.family: root.pick(root.themeObj.typography || ({}), "font_family", "Sans Serif")
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            text: root.value
            color: root.pick(cardStyleObj, "value_color", root.pick(root.colors(), "accent", "#22D3EE"))
            font.pixelSize: Number(root.pick(cardStyleObj, "value_size", 24))
            font.bold: true
            font.family: root.pick(root.themeObj.typography || ({}), "font_family", "Sans Serif")
            elide: Text.ElideRight
        }
    }

    // TASK25B DesignMetricCard enlarges HUD metrics through design-pack sizing tokens.
}
