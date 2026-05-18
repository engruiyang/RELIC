import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property string label: ""
    property string value: ""
    property var themeObj: ({})
    property var cardStyleObj: ({})
    property var metricStyleObj: ({})

    implicitWidth: Number(styleValue(effectiveStyle(), "metric_width", styleValue(effectiveStyle(), "width", 170)))
    implicitHeight: Number(styleValue(effectiveStyle(), "metric_height", styleValue(effectiveStyle(), "height", 92)))
    width: implicitWidth
    height: implicitHeight

    function effectiveStyle() {
        var card = root.cardStyleObj || ({})
        if (Object.keys(card).length > 0) {
            return card
        }
        return root.metricStyleObj || ({})
    }

    function styleValue(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    readonly property var colorsObj: themeObj.colors || ({})
    readonly property var styleObj: effectiveStyle()

    color: styleValue(styleObj, "metric_card_background", styleValue(styleObj, "background", styleValue(colorsObj, "panel", "#FFFFFF")))
    border.color: styleValue(styleObj, "metric_card_border", styleValue(styleObj, "border", styleValue(colorsObj, "panel_border", "#CBD5E1")))
    border.width: Number(styleValue(styleObj, "border_width", 1))
    radius: Number(styleValue(styleObj, "radius", 10))

    Column {
        anchors.fill: parent
        anchors.margins: Number(root.styleValue(root.styleObj, "padding", 10))
        spacing: 4

        Text {
            width: parent.width
            text: root.label
            color: root.styleValue(root.styleObj, "metric_title_color", root.styleValue(root.colorsObj, "text_muted", "#475569"))
            font.pixelSize: Number(root.styleValue(root.styleObj, "metric_title_size", ((root.themeObj.typography || ({})).hud_label_size || 12)))
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            text: root.value
            color: root.styleValue(root.styleObj, "metric_value_color", root.styleValue(root.colorsObj, "text", "#0F172A"))
            font.pixelSize: Number(root.styleValue(root.styleObj, "metric_value_size", ((root.themeObj.typography || ({})).hud_value_size || 24)))
            font.bold: true
            elide: Text.ElideRight
        }
    }

    // TASK25B/TASK25C metric card accepts both cardStyleObj and metricStyleObj for compatibility.
}
