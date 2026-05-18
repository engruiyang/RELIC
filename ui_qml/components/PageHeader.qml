import QtQuick
import QtQuick.Controls

Column {
    property string titleText: ""
    property string subtitleText: ""
    property var designThemeObj: ({})
    property var componentStyleObj: ({})
    property var headerStyleObj: ({})
    spacing: 2

    readonly property color textColor: (designThemeObj.colors && designThemeObj.colors.text) ? designThemeObj.colors.text : "#0F172A"
    readonly property color mutedTextColor: (designThemeObj.colors && designThemeObj.colors.text_muted) ? designThemeObj.colors.text_muted : "#475569"

    Label { text: titleText; font.pixelSize: 20; font.bold: true; color: textColor }
    Label { text: subtitleText; color: mutedTextColor; wrapMode: Text.WordWrap }
}
