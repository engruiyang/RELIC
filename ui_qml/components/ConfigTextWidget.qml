import QtQuick 2.15

Item {
    id: root

    property string label: ""
    property string value: ""
    property string fallback: "n/a"
    property string unit: ""
    property color labelColor: "#8EA4BF"
    property color textColor: "#EAF2FF"
    property int labelSize: 11
    property int textSize: 14

    readonly property string displayValue: value.length > 0 ? value : fallback
    readonly property string displayText: unit.length > 0 && displayValue !== fallback ? displayValue + " " + unit : displayValue

    implicitWidth: 180
    implicitHeight: label.length > 0 ? 42 : 24

    Column {
        anchors.fill: parent
        spacing: 2

        Text {
            width: parent.width
            text: root.label
            visible: root.label.length > 0
            color: root.labelColor
            font.pixelSize: root.labelSize
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            text: root.displayText
            color: root.textColor
            font.pixelSize: root.textSize
            elide: Text.ElideRight
        }
    }
}
