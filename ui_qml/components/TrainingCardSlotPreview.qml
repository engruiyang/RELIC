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
    property string rectText: "n/a"
    property int widgetCount: 0
    property string actionIdsText: "n/a"
    property string sourceRootsText: "n/a"
    property string firstWidgetLabelsText: "n/a"
    property bool placeholder: false
    property string roleText: ""

    implicitWidth: 760
    implicitHeight: 140

    DesignCard {
        anchors.fill: parent
        cardTitle: "Training Slot " + String(root.slotIndex) + " · " + root.cardId
        cardSubtitle: root.cardTitleText
        backgroundColor: root.placeholder ? "#1F2937" : "#111827"
        borderColor: root.placeholder ? "#F59E0B" : "#334155"

        Column {
            anchors.fill: parent
            spacing: 6

            Row {
                width: parent.width
                spacing: 8

                ConfigTextWidget { width: (parent.width - 24) / 4; label: "Type"; value: root.cardType }
                ConfigTextWidget { width: (parent.width - 24) / 4; label: "Required"; value: root.requiredCard ? "true" : "false" }
                ConfigTextWidget { width: (parent.width - 24) / 4; label: "Locked"; value: root.lockedCard ? "true" : "false" }
                ConfigTextWidget { width: (parent.width - 24) / 4; label: "Widgets"; value: String(root.widgetCount) }
            }

            Row {
                width: parent.width
                spacing: 8

                ConfigTextWidget { width: (parent.width - 16) / 3; label: "Rect"; value: root.rectText }
                ConfigTextWidget { width: (parent.width - 16) / 3; label: "Placeholder"; value: root.placeholder ? "true" : "false" }
                ConfigTextWidget { width: (parent.width - 16) / 3; label: "Role"; value: root.roleText.length > 0 ? root.roleText : "n/a" }
            }

            Row {
                width: parent.width
                spacing: 8

                ConfigTextWidget { width: (parent.width - 16) / 3; label: "Actions"; value: root.actionIdsText }
                ConfigTextWidget { width: (parent.width - 16) / 3; label: "Source Roots"; value: root.sourceRootsText }
                ConfigTextWidget { width: (parent.width - 16) / 3; label: "First Widgets"; value: root.firstWidgetLabelsText }
            }
        }
    }
}
