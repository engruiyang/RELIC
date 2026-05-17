import QtQuick
import QtQuick.Controls
Column {
    property string titleText: ""
    property string subtitleText: ""
    spacing: 2
    Label { text: titleText; font.pixelSize: 20; font.bold: true; color: "#e6edf5" }
    Label { text: subtitleText; color: "#9aacbd"; wrapMode: Text.WordWrap }
}
