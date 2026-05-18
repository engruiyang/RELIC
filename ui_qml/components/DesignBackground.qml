import QtQuick
import QtQuick.Controls

Item {
    id: root
    property var themeObj: ({})
    property var styleObj: ({})
    property var renderResourcesObj: ({})
    property color fallbackColor: "#F8FAFC"

    readonly property var layered: (styleObj && styleObj.layered) ? styleObj.layered : ({})
    readonly property color bgColor: layered.color || fallbackColor
    readonly property real bgOpacity: layered.opacity !== undefined ? Number(layered.opacity) : 1.0

    Rectangle { anchors.fill: parent; color: bgColor; opacity: bgOpacity }
    Rectangle {
        anchors.fill: parent
        color: (layered.overlay && layered.overlay.color) ? layered.overlay.color : "transparent"
        opacity: (layered.overlay && layered.overlay.opacity !== undefined) ? Number(layered.overlay.opacity) : 0
    }
}
