import QtQuick
import QtQuick.Controls

Rectangle {
    property var themeObj: ({})
    color: (themeObj.colors && themeObj.colors.panel) ? themeObj.colors.panel : "#FFFFFF"
    border.color: (themeObj.colors && themeObj.colors.panel_border) ? themeObj.colors.panel_border : "#CBD5E1"
    radius: 8
}
