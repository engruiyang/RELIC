import QtQuick 2.15

Item {
    id: root

    property string label: ""
    property string value: ""
    property string fallback: "n/a"
    property string unit: ""
    property string level: "normal"

    property int freshnessAgeMs: -1
    property int okMaxAgeMs: 1000
    property int warningMaxAgeMs: 3000

    property color labelColor: "#8EA4BF"
    property color normalColor: "#EAF2FF"
    property color okColor: "#9BE7C0"
    property color warningColor: "#FFD479"
    property color dangerColor: "#FF7A7A"

    readonly property string freshnessLevel: freshnessAgeMs < 0 ? level
        : freshnessAgeMs <= okMaxAgeMs ? "ok"
        : freshnessAgeMs <= warningMaxAgeMs ? "warning"
        : "danger"

    readonly property color valueColor: freshnessLevel === "danger" ? dangerColor
        : freshnessLevel === "warning" ? warningColor
        : freshnessLevel === "ok" ? okColor
        : normalColor

    readonly property string displayValue: value.length > 0 ? value : fallback
    readonly property string displayText: unit.length > 0 && displayValue !== fallback ? displayValue + " " + unit : displayValue

    implicitWidth: 160
    implicitHeight: 58

    Rectangle {
        anchors.fill: parent
        color: "#00000000"
        border.color: "#223044"
        border.width: 1
        radius: 10
    }

    Column {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 4

        Text {
            width: parent.width
            text: root.label
            color: root.labelColor
            font.pixelSize: 11
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            text: root.displayText
            color: root.valueColor
            font.pixelSize: 18
            font.bold: true
            elide: Text.ElideRight
        }
    }
}
