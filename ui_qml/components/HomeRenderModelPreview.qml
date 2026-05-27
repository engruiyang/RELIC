import QtQuick 2.15

Item {
    id: root

    property string pageId: "home"
    property int cardCount: 0
    property int widgetCount: 0
    property int requiredCardCount: 0
    property int lockedCardCount: 0
    property string actionsText: "n/a"
    property string sourceRootsText: "n/a"
    property string cardIdsText: "n/a"

    implicitWidth: 760
    implicitHeight: 360

    DesignCard {
        anchors.fill: parent
        cardTitle: "Home Render Model Preview"
        cardSubtitle: "TASK26E-1 summary-only preview"
        backgroundColor: "#111A25"
        borderColor: "#3B5674"

        Column {
            anchors.fill: parent
            spacing: 6

            ConfigTextWidget { width: parent.width; label: "Page"; value: root.pageId }
            ConfigTextWidget { width: parent.width; label: "Cards"; value: String(root.cardCount) }
            ConfigTextWidget { width: parent.width; label: "Widgets"; value: String(root.widgetCount) }
            ConfigTextWidget { width: parent.width; label: "Required Cards"; value: String(root.requiredCardCount) }
            ConfigTextWidget { width: parent.width; label: "Locked Cards"; value: String(root.lockedCardCount) }
            ConfigTextWidget { width: parent.width; label: "Actions"; value: root.actionsText }
            ConfigTextWidget { width: parent.width; label: "Source Roots"; value: root.sourceRootsText }
            ConfigTextWidget { width: parent.width; label: "Card IDs"; value: root.cardIdsText }
        }
    }
}
