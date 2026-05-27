import QtQuick 2.15

Rectangle {
    id: root

    property string cardTitle: ""
    property string cardSubtitle: ""
    property string cardMode: "normal"

    property color backgroundColor: "#151B24"
    property real backgroundOpacity: 0.92
    property string backgroundImage: ""

    property color borderColor: "#2B3A4C"
    property int borderWidth: 1
    property int radiusValue: 16
    property int paddingValue: 14

    property color titleColor: "#EAF2FF"
    property color subtitleColor: "#8EA4BF"
    property color bodyColor: "#D7E2F0"

    property string shapeType: "rounded_rect"

    default property alias contentData: body.data

    color: "transparent"
    radius: shapeType === "pill" ? height / 2 : radiusValue
    border.width: 0
    clip: true

    Rectangle {
        id: backgroundLayer
        anchors.fill: parent
        color: root.backgroundColor
        opacity: root.backgroundOpacity
        radius: root.shapeType === "pill" ? height / 2 : root.radiusValue
        border.color: root.borderColor
        border.width: root.borderWidth
    }

    Image {
        id: backgroundImageLayer
        anchors.fill: parent
        source: root.backgroundImage
        visible: root.backgroundImage.length > 0
        fillMode: Image.PreserveAspectCrop
        opacity: 0.36
        asynchronous: true
        cache: true
    }

    Column {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: root.paddingValue
        spacing: 8

        Column {
            id: headerBlock
            width: parent.width
            spacing: 2
            visible: root.cardTitle.length > 0 || root.cardSubtitle.length > 0

            Text {
                id: titleText
                width: parent.width
                text: root.cardTitle
                visible: root.cardTitle.length > 0
                color: root.titleColor
                font.pixelSize: 17
                font.bold: true
                elide: Text.ElideRight
            }

            Text {
                id: subtitleText
                width: parent.width
                text: root.cardSubtitle
                visible: root.cardSubtitle.length > 0
                color: root.subtitleColor
                font.pixelSize: 12
                elide: Text.ElideRight
                wrapMode: Text.NoWrap
            }
        }

        Item {
            id: body
            width: parent.width
            height: Math.max(0, parent.height - headerBlock.height - contentColumn.spacing)
        }
    }
}
