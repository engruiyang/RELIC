import QtQuick 2.15
import QtQuick.Controls.Basic as Basic

Basic.ComboBox {
    id: root

    property string optionsText: ""
    property string fallbackText: ""
    property int textPixelSize: 11
    property int itemHeight: 26
    property real cornerRadius: 10
    property real popupCornerRadius: Math.max(10, cornerRadius)
    property real popupMaxHeight: 168
    property color backgroundColor: "#182130"
    property color textColor: "#EAF2FF"
    property color mutedTextColor: "#8EA4BF"
    property color borderColor: "#465A78"
    property color popupBackgroundColor: "#121926"
    property color popupBorderColor: borderColor
    property color itemHoverColor: "#24324A"
    property color itemCurrentColor: "#2D3E5E"
    property color selectedTextColor: "#FFFFFF"
    property real popupOpacity: 0.98

    function optionsFromText(text, fallbackValue) {
        var source = text && text.length > 0 ? text : fallbackValue
        if (!source || source.length === 0) return []
        var raw = String(source).split("|")
        var out = []
        for (var i = 0; i < raw.length; i += 1) {
            var value = String(raw[i]).trim()
            if (value.length > 0) out.push(value)
        }
        return out
    }

    model: optionsFromText(optionsText, fallbackText)
    font.pixelSize: textPixelSize
    clip: false

    onModelChanged: {
        if (count > 0 && currentIndex < 0) {
            currentIndex = 0
        }
    }

    Component.onCompleted: {
        if (count > 0 && currentIndex < 0) {
            currentIndex = 0
        }
    }

    background: Rectangle {
        radius: root.cornerRadius
        color: root.backgroundColor
        border.color: root.borderColor
        border.width: 1
        opacity: 0.98
    }

    contentItem: Text {
        leftPadding: 10
        rightPadding: 28
        verticalAlignment: Text.AlignVCenter
        text: root.displayText && root.displayText.length > 0 ? root.displayText : (root.count > 0 ? root.textAt(root.currentIndex >= 0 ? root.currentIndex : 0) : "")
        color: root.textColor
        font.pixelSize: root.textPixelSize
        elide: Text.ElideRight
        maximumLineCount: 1
    }

    indicator: Text {
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.verticalCenter: parent.verticalCenter
        text: root.popup.visible ? "▴" : "▾"
        color: root.mutedTextColor
        font.pixelSize: Math.max(9, root.textPixelSize)
    }

    delegate: Basic.ItemDelegate {
        id: optionDelegate
        width: root.width
        height: root.itemHeight
        hoverEnabled: true
        highlighted: root.highlightedIndex === index

        contentItem: Text {
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            text: index >= 0 ? root.textAt(index) : ""
            color: optionDelegate.highlighted || optionDelegate.hovered ? root.selectedTextColor : root.textColor
            font.pixelSize: root.textPixelSize
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            maximumLineCount: 1
            opacity: 1.0
        }

        background: Rectangle {
            radius: Math.max(6, root.popupCornerRadius - 4)
            color: optionDelegate.highlighted ? root.itemCurrentColor : (optionDelegate.hovered ? root.itemHoverColor : "transparent")
            opacity: 1.0
        }
    }

    popup: Basic.Popup {
        y: root.height + 4
        width: root.width
        height: Math.min(Math.max(1, root.count) * (root.itemHeight + 2) + 8, root.popupMaxHeight)
        implicitHeight: height
        padding: 4
        clip: true

        background: Rectangle {
            radius: root.popupCornerRadius
            color: root.popupBackgroundColor
            opacity: root.popupOpacity
            border.color: root.popupBorderColor
            border.width: 1
        }

        contentItem: ListView {
            id: popupList
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            model: root.delegateModel
            currentIndex: root.highlightedIndex
            spacing: 2
            interactive: contentHeight > height
        }
    }
}
