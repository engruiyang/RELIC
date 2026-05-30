import QtQuick 2.15

Item {
    id: root

    property int slotCount: 7

    property string slot1CardId: "training_control_card"
    property string slot1CardType: ""
    property string slot1Title: "training_control_card"
    property string slot1Subtitle: ""
    property bool slot1Required: true
    property bool slot1Locked: true
    property string slot1RectText: "n/a"
    property int slot1WidgetCount: 0
    property string slot1ActionIdsText: "n/a"
    property string slot1SourceRootsText: "n/a"
    property string slot1FirstWidgetLabelsText: "n/a"
    property bool slot1Placeholder: false
    property string slot1RoleText: ""

    property string slot2CardId: "session_card"
    property string slot2CardType: ""
    property string slot2Title: "session_card"
    property string slot2Subtitle: ""
    property bool slot2Required: true
    property bool slot2Locked: true
    property string slot2RectText: "n/a"
    property int slot2WidgetCount: 0
    property string slot2ActionIdsText: "n/a"
    property string slot2SourceRootsText: "n/a"
    property string slot2FirstWidgetLabelsText: "n/a"
    property bool slot2Placeholder: false
    property string slot2RoleText: ""

    property string slot3CardId: "runtime_io_card"
    property string slot3CardType: ""
    property string slot3Title: "runtime_io_card"
    property string slot3Subtitle: ""
    property bool slot3Required: true
    property bool slot3Locked: true
    property string slot3RectText: "n/a"
    property int slot3WidgetCount: 0
    property string slot3ActionIdsText: "n/a"
    property string slot3SourceRootsText: "n/a"
    property string slot3FirstWidgetLabelsText: "n/a"
    property bool slot3Placeholder: false
    property string slot3RoleText: ""

    property string slot4CardId: "calibration_status_card"
    property string slot4CardType: ""
    property string slot4Title: "calibration_status_card"
    property string slot4Subtitle: ""
    property bool slot4Required: true
    property bool slot4Locked: true
    property string slot4RectText: "n/a"
    property int slot4WidgetCount: 0
    property string slot4ActionIdsText: "n/a"
    property string slot4SourceRootsText: "n/a"
    property string slot4FirstWidgetLabelsText: "n/a"
    property bool slot4Placeholder: false
    property string slot4RoleText: ""

    property string slot5CardId: "game_hud_card"
    property string slot5CardType: ""
    property string slot5Title: "game_hud_card"
    property string slot5Subtitle: ""
    property bool slot5Required: true
    property bool slot5Locked: true
    property string slot5RectText: "n/a"
    property int slot5WidgetCount: 0
    property string slot5ActionIdsText: "n/a"
    property string slot5SourceRootsText: "n/a"
    property string slot5FirstWidgetLabelsText: "n/a"
    property bool slot5Placeholder: false
    property string slot5RoleText: ""

    property string slot6CardId: "game_canvas_card"
    property string slot6CardType: ""
    property string slot6Title: "game_canvas_card"
    property string slot6Subtitle: ""
    property bool slot6Required: true
    property bool slot6Locked: true
    property string slot6RectText: "n/a"
    property int slot6WidgetCount: 0
    property string slot6ActionIdsText: "n/a"
    property string slot6SourceRootsText: "n/a"
    property string slot6FirstWidgetLabelsText: "n/a"
    property bool slot6Placeholder: false
    property string slot6RoleText: ""

    property string slot7CardId: "diagnostics_summary_card"
    property string slot7CardType: ""
    property string slot7Title: "diagnostics_summary_card"
    property string slot7Subtitle: ""
    property bool slot7Required: true
    property bool slot7Locked: true
    property string slot7RectText: "n/a"
    property int slot7WidgetCount: 0
    property string slot7ActionIdsText: "n/a"
    property string slot7SourceRootsText: "n/a"
    property string slot7FirstWidgetLabelsText: "n/a"
    property bool slot7Placeholder: false
    property string slot7RoleText: ""

    implicitWidth: 760
    implicitHeight: 1080

    DesignCard {
        anchors.fill: parent
        cardTitle: "Training Card Slots Preview"
        cardSubtitle: "TASK26F-2 renderResources injection preview"
        backgroundColor: "#0F172A"
        borderColor: "#475569"

        Column {
            anchors.fill: parent
            spacing: 8

            TrainingCardSlotPreview {
                width: parent.width
                height: 132
                slotIndex: 1
                cardId: root.slot1CardId
                cardType: root.slot1CardType
                cardTitleText: root.slot1Title
                cardSubtitleText: root.slot1Subtitle
                requiredCard: root.slot1Required
                lockedCard: root.slot1Locked
                rectText: root.slot1RectText
                widgetCount: root.slot1WidgetCount
                actionIdsText: root.slot1ActionIdsText
                sourceRootsText: root.slot1SourceRootsText
                firstWidgetLabelsText: root.slot1FirstWidgetLabelsText
                placeholder: root.slot1Placeholder
                roleText: root.slot1RoleText
            }

            TrainingCardSlotPreview {
                width: parent.width
                height: 132
                slotIndex: 2
                cardId: root.slot2CardId
                cardType: root.slot2CardType
                cardTitleText: root.slot2Title
                cardSubtitleText: root.slot2Subtitle
                requiredCard: root.slot2Required
                lockedCard: root.slot2Locked
                rectText: root.slot2RectText
                widgetCount: root.slot2WidgetCount
                actionIdsText: root.slot2ActionIdsText
                sourceRootsText: root.slot2SourceRootsText
                firstWidgetLabelsText: root.slot2FirstWidgetLabelsText
                placeholder: root.slot2Placeholder
                roleText: root.slot2RoleText
            }

            TrainingCardSlotPreview {
                width: parent.width
                height: 132
                slotIndex: 3
                cardId: root.slot3CardId
                cardType: root.slot3CardType
                cardTitleText: root.slot3Title
                cardSubtitleText: root.slot3Subtitle
                requiredCard: root.slot3Required
                lockedCard: root.slot3Locked
                rectText: root.slot3RectText
                widgetCount: root.slot3WidgetCount
                actionIdsText: root.slot3ActionIdsText
                sourceRootsText: root.slot3SourceRootsText
                firstWidgetLabelsText: root.slot3FirstWidgetLabelsText
                placeholder: root.slot3Placeholder
                roleText: root.slot3RoleText
            }

            TrainingCardSlotPreview {
                width: parent.width
                height: 132
                slotIndex: 4
                cardId: root.slot4CardId
                cardType: root.slot4CardType
                cardTitleText: root.slot4Title
                cardSubtitleText: root.slot4Subtitle
                requiredCard: root.slot4Required
                lockedCard: root.slot4Locked
                rectText: root.slot4RectText
                widgetCount: root.slot4WidgetCount
                actionIdsText: root.slot4ActionIdsText
                sourceRootsText: root.slot4SourceRootsText
                firstWidgetLabelsText: root.slot4FirstWidgetLabelsText
                placeholder: root.slot4Placeholder
                roleText: root.slot4RoleText
            }

            TrainingCardSlotPreview {
                width: parent.width
                height: 132
                slotIndex: 5
                cardId: root.slot5CardId
                cardType: root.slot5CardType
                cardTitleText: root.slot5Title
                cardSubtitleText: root.slot5Subtitle
                requiredCard: root.slot5Required
                lockedCard: root.slot5Locked
                rectText: root.slot5RectText
                widgetCount: root.slot5WidgetCount
                actionIdsText: root.slot5ActionIdsText
                sourceRootsText: root.slot5SourceRootsText
                firstWidgetLabelsText: root.slot5FirstWidgetLabelsText
                placeholder: root.slot5Placeholder
                roleText: root.slot5RoleText
            }

            TrainingCardSlotPreview {
                width: parent.width
                height: 132
                slotIndex: 6
                cardId: root.slot6CardId
                cardType: root.slot6CardType
                cardTitleText: root.slot6Title
                cardSubtitleText: root.slot6Subtitle
                requiredCard: root.slot6Required
                lockedCard: root.slot6Locked
                rectText: root.slot6RectText
                widgetCount: root.slot6WidgetCount
                actionIdsText: root.slot6ActionIdsText
                sourceRootsText: root.slot6SourceRootsText
                firstWidgetLabelsText: root.slot6FirstWidgetLabelsText
                placeholder: root.slot6Placeholder
                roleText: root.slot6RoleText
            }

            TrainingCardSlotPreview {
                width: parent.width
                height: 132
                slotIndex: 7
                cardId: root.slot7CardId
                cardType: root.slot7CardType
                cardTitleText: root.slot7Title
                cardSubtitleText: root.slot7Subtitle
                requiredCard: root.slot7Required
                lockedCard: root.slot7Locked
                rectText: root.slot7RectText
                widgetCount: root.slot7WidgetCount
                actionIdsText: root.slot7ActionIdsText
                sourceRootsText: root.slot7SourceRootsText
                firstWidgetLabelsText: root.slot7FirstWidgetLabelsText
                placeholder: root.slot7Placeholder
                roleText: root.slot7RoleText
            }

        }
    }
}