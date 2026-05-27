import QtQuick 2.15

Item {
    id: root

    property int slotCount: 4

    property string slot1CardId: "runtime_io_card"
    property string slot1CardType: "runtime"
    property string slot1Title: "Runtime I/O"
    property string slot1Subtitle: "Connection and stream health"
    property bool slot1Required: true
    property bool slot1Locked: true
    property string slot1RectText: "x=10, y=10, w=386, h=290"
    property int slot1WidgetCount: 3
    property string slot1ActionIdsText: "n/a"
    property string slot1SourceRootsText: "runtimeSnapshot"
    property string slot1FirstWidgetLabelsText: "Runtime, Stream, Attention"

    property string slot2CardId: "quick_actions_card"
    property string slot2CardType: "actions"
    property string slot2Title: "Quick Actions"
    property string slot2Subtitle: "Safety and refresh"
    property bool slot2Required: true
    property bool slot2Locked: true
    property string slot2RectText: "x=404, y=10, w=386, h=290"
    property int slot2WidgetCount: 2
    property string slot2ActionIdsText: "app.refresh_now, live.safe_stop"
    property string slot2SourceRootsText: "n/a"
    property string slot2FirstWidgetLabelsText: "Refresh, Safe Stop"

    property string slot3CardId: "recent_session_card"
    property string slot3CardType: "session"
    property string slot3Title: "Recent Session"
    property string slot3Subtitle: "Session summary"
    property bool slot3Required: false
    property bool slot3Locked: false
    property string slot3RectText: "x=10, y=308, w=584, h=290"
    property int slot3WidgetCount: 3
    property string slot3ActionIdsText: "n/a"
    property string slot3SourceRootsText: "gameHudJson, sessionState"
    property string slot3FirstWidgetLabelsText: "Active, Session ID, HUD"

    property string slot4CardId: "relic_identity_card"
    property string slot4CardType: "identity"
    property string slot4Title: "RELIC Identity"
    property string slot4Subtitle: "Brand and visual"
    property bool slot4Required: false
    property bool slot4Locked: false
    property string slot4RectText: "x=798, y=10, w=386, h=588"
    property int slot4WidgetCount: 2
    property string slot4ActionIdsText: "n/a"
    property string slot4SourceRootsText: "renderResourcesJson"
    property string slot4FirstWidgetLabelsText: "Identity, Tagline"

    implicitWidth: 760
    implicitHeight: 520

    DesignCard {
        anchors.fill: parent
        cardTitle: "Home Card Slots Preview"
        cardSubtitle: "TASK26E-3 controlled injection preview"
        backgroundColor: "#101824"
        borderColor: "#44607E"

        Column {
            anchors.fill: parent
            spacing: 8

            HomeCardSlotPreview {
                width: parent.width
                slotIndex: 1
                cardId: root.slot1CardId === "" ? "empty_slot" : root.slot1CardId
                cardType: root.slot1CardType
                cardTitleText: root.slot1Title
                cardSubtitleText: root.slot1Subtitle
                requiredCard: root.slot1Required
                lockedCard: root.slot1Locked
                modelX: 10
                modelY: 10
                modelWidth: 386
                modelHeight: 290
                widgetCount: root.slot1WidgetCount
                actionIdsText: root.slot1ActionIdsText
                sourceRootsText: root.slot1SourceRootsText
                firstWidgetLabelsText: root.slot1FirstWidgetLabelsText
            }

            HomeCardSlotPreview {
                width: parent.width
                slotIndex: 2
                cardId: root.slot2CardId === "" ? "empty_slot" : root.slot2CardId
                cardType: root.slot2CardType
                cardTitleText: root.slot2Title
                cardSubtitleText: root.slot2Subtitle
                requiredCard: root.slot2Required
                lockedCard: root.slot2Locked
                modelX: 404
                modelY: 10
                modelWidth: 386
                modelHeight: 290
                widgetCount: root.slot2WidgetCount
                actionIdsText: root.slot2ActionIdsText
                sourceRootsText: root.slot2SourceRootsText
                firstWidgetLabelsText: root.slot2FirstWidgetLabelsText
            }

            HomeCardSlotPreview {
                width: parent.width
                slotIndex: 3
                cardId: root.slot3CardId === "" ? "empty_slot" : root.slot3CardId
                cardType: root.slot3CardType
                cardTitleText: root.slot3Title
                cardSubtitleText: root.slot3Subtitle
                requiredCard: root.slot3Required
                lockedCard: root.slot3Locked
                modelX: 10
                modelY: 308
                modelWidth: 584
                modelHeight: 290
                widgetCount: root.slot3WidgetCount
                actionIdsText: root.slot3ActionIdsText
                sourceRootsText: root.slot3SourceRootsText
                firstWidgetLabelsText: root.slot3FirstWidgetLabelsText
            }

            HomeCardSlotPreview {
                width: parent.width
                slotIndex: 4
                cardId: root.slot4CardId === "" ? "empty_slot" : root.slot4CardId
                cardType: root.slot4CardType
                cardTitleText: root.slot4Title
                cardSubtitleText: root.slot4Subtitle
                requiredCard: root.slot4Required
                lockedCard: root.slot4Locked
                modelX: 798
                modelY: 10
                modelWidth: 386
                modelHeight: 588
                widgetCount: root.slot4WidgetCount
                actionIdsText: root.slot4ActionIdsText
                sourceRootsText: root.slot4SourceRootsText
                firstWidgetLabelsText: root.slot4FirstWidgetLabelsText
            }
        }
    }
}
