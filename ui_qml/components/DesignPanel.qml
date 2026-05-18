import QtQuick
import QtQuick.Controls

Rectangle {
    property var themeObj: ({})
    property var panelStyleObj: ({})
    color: panelStyleObj.background || (themeObj.colors ? themeObj.colors.panel : "#FFFFFF")
    border.color: panelStyleObj.border || (themeObj.colors ? themeObj.colors.panel_border : "#CBD5E1")
    border.width: 1
    radius: panelStyleObj.radius !== undefined ? Number(panelStyleObj.radius) : 10
    opacity: panelStyleObj.opacity !== undefined ? Number(panelStyleObj.opacity) : 0.96
}
