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

    property int titlePixelSize: 17
    property int subtitlePixelSize: 12
    property int headerSpacing: 2
    property int contentSpacing: 8

    property string shapeType: "rounded_rect"
    property bool glassEnabled: false
    property color glassTintColor: "#DDEEFF"
    property real glassOpacity: 0.0
    property bool glassHighlight: false

    default property alias contentData: body.data

    function effectiveRadius() {
        if (root.shapeType === "pill") {
            return height / 2
        }
        if (root.shapeType === "rect") {
            return 0
        }
        return root.radiusValue
    }

    color: "transparent"
    radius: effectiveRadius()
    border.width: 0
    clip: true

    Rectangle {
        id: backgroundLayer
        anchors.fill: parent
        color: root.backgroundColor
        opacity: root.backgroundOpacity
        radius: root.effectiveRadius()
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

    Rectangle {
        id: glassTintLayer
        anchors.fill: parent
        visible: root.glassEnabled
        color: root.glassTintColor
        opacity: root.glassOpacity
        radius: root.effectiveRadius()
    }

    Rectangle {
        id: glassTopHighlight
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: Math.max(1, root.borderWidth + 1)
        visible: root.glassEnabled && root.glassHighlight
        color: "#FFFFFF"
        opacity: 0.28
    }

    Rectangle {
        id: glassLeftHighlight
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: Math.max(1, root.borderWidth + 1)
        visible: root.glassEnabled && root.glassHighlight
        color: "#FFFFFF"
        opacity: 0.10
    }

    Column {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: root.paddingValue
        spacing: root.contentSpacing

        Column {
            id: headerBlock
            width: parent.width
            spacing: root.headerSpacing
            visible: root.cardTitle.length > 0 || root.cardSubtitle.length > 0

            Text {
                id: titleText
                width: parent.width
                text: root.cardTitle
                visible: root.cardTitle.length > 0
                color: root.titleColor
                font.pixelSize: root.titlePixelSize
                font.bold: true
                elide: Text.ElideRight
            }

            Text {
                id: subtitleText
                width: parent.width
                text: root.cardSubtitle
                visible: root.cardSubtitle.length > 0
                color: root.subtitleColor
                font.pixelSize: root.subtitlePixelSize
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
