import QtQuick 2.15

Item {
    id: root

    property string slotLabelPrefix: "Slot"
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

    property string layoutMode: "stack"
    property color backgroundColor: "#121B27"
    property color borderColor: "#35516F"
    property color placeholderBackgroundColor: "#1F2937"
    property color placeholderBorderColor: "#F59E0B"

    implicitWidth: 760
    implicitHeight: layoutMode === "grid" ? 140 : 120

    readonly property string effectiveRoleText: root.roleText.length > 0 ? root.roleText : "n/a"
    readonly property color effectiveBackgroundColor: root.placeholder ? root.placeholderBackgroundColor : root.backgroundColor
    readonly property color effectiveBorderColor: root.placeholder ? root.placeholderBorderColor : root.borderColor

    DesignCard {
        anchors.fill: parent
        cardTitle: root.slotLabelPrefix + " " + String(root.slotIndex) + " · " + root.cardId
        cardSubtitle: root.cardTitleText
        backgroundColor: root.effectiveBackgroundColor
        borderColor: root.effectiveBorderColor

        Column {
            anchors.fill: parent
            spacing: 3
            visible: root.layoutMode !== "grid"

            ConfigTextWidget { width: parent.width; label: "Type"; value: root.cardType }
            ConfigTextWidget { width: parent.width; label: "Required"; value: root.requiredCard ? "true" : "false" }
            ConfigTextWidget { width: parent.width; label: "Locked"; value: root.lockedCard ? "true" : "false" }
            ConfigTextWidget { width: parent.width; label: "Rect"; value: root.rectText }
            ConfigTextWidget { width: parent.width; label: "Widgets"; value: String(root.widgetCount) }
            ConfigTextWidget { width: parent.width; label: "Actions"; value: root.actionIdsText }
            ConfigTextWidget { width: parent.width; label: "Source Roots"; value: root.sourceRootsText }
            ConfigTextWidget { width: parent.width; label: "First Widgets"; value: root.firstWidgetLabelsText }
        }

        Column {
            anchors.fill: parent
            spacing: 6
            visible: root.layoutMode === "grid"

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
                ConfigTextWidget { width: (parent.width - 16) / 3; label: "Role"; value: root.effectiveRoleText }
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
