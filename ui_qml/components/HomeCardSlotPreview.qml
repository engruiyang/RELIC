import QtQuick 2.15

Item {
    id: root

    property int slotIndex: 0
    property string cardId: ""
    property string cardType: ""
    property string cardTitleText: ""
    property string cardSubtitleText: ""
    property bool requiredCard: false
    property bool lockedCard: false
    property real modelX: 0
    property real modelY: 0
    property real modelWidth: 0
    property real modelHeight: 0
    property int widgetCount: 0
    property string actionIdsText: "n/a"
    property string sourceRootsText: "n/a"
    property string firstWidgetLabelsText: "n/a"

    implicitWidth: 560
    implicitHeight: 120

    DesignCard {
        anchors.fill: parent
        cardTitle: "Slot " + root.slotIndex + " · " + root.cardId
        cardSubtitle: root.cardTitleText
        backgroundColor: "#121B27"
        borderColor: "#35516F"

        Column {
            anchors.fill: parent
            spacing: 3
            ConfigTextWidget { width: parent.width; label: "Type"; value: root.cardType }
            ConfigTextWidget { width: parent.width; label: "Required"; value: root.requiredCard ? "true" : "false" }
            ConfigTextWidget { width: parent.width; label: "Locked"; value: root.lockedCard ? "true" : "false" }
            ConfigTextWidget { width: parent.width; label: "Model Rect"; value: "x=" + root.modelX + ", y=" + root.modelY + ", w=" + root.modelWidth + ", h=" + root.modelHeight }
            ConfigTextWidget { width: parent.width; label: "Widgets"; value: String(root.widgetCount) }
            ConfigTextWidget { width: parent.width; label: "Actions"; value: root.actionIdsText }
            ConfigTextWidget { width: parent.width; label: "Source Roots"; value: root.sourceRootsText }
            ConfigTextWidget { width: parent.width; label: "First Widgets"; value: root.firstWidgetLabelsText }
        }
    }
}
