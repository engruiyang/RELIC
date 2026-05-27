import QtQuick 2.15

Item {
    id: root

    implicitWidth: 760
    implicitHeight: 520

    DesignCard {
        anchors.fill: parent
        cardTitle: "Home Card Slots Preview"
        cardSubtitle: "TASK26E-2 fixed 4 slots preview"
        backgroundColor: "#101824"
        borderColor: "#44607E"

        Column {
            anchors.fill: parent
            spacing: 8

            HomeCardSlotPreview {
                width: parent.width
                slotIndex: 1
                cardId: "runtime_io_card"
                cardType: "runtime"
                cardTitleText: "Runtime I/O"
                cardSubtitleText: "Connection and stream health"
                requiredCard: true
                lockedCard: true
                modelX: 10
                modelY: 10
                modelWidth: 386
                modelHeight: 290
                widgetCount: 3
                actionIdsText: "n/a"
                sourceRootsText: "runtimeSnapshot"
                firstWidgetLabelsText: "Runtime, Stream, Attention"
            }

            HomeCardSlotPreview {
                width: parent.width
                slotIndex: 2
                cardId: "quick_actions_card"
                cardType: "actions"
                cardTitleText: "Quick Actions"
                cardSubtitleText: "Safety and refresh"
                requiredCard: true
                lockedCard: true
                modelX: 404
                modelY: 10
                modelWidth: 386
                modelHeight: 290
                widgetCount: 2
                actionIdsText: "app.refresh_now, live.safe_stop"
                sourceRootsText: "n/a"
                firstWidgetLabelsText: "Refresh, Safe Stop"
            }

            HomeCardSlotPreview {
                width: parent.width
                slotIndex: 3
                cardId: "recent_session_card"
                cardType: "session"
                cardTitleText: "Recent Session"
                cardSubtitleText: "Session summary"
                requiredCard: false
                lockedCard: false
                modelX: 10
                modelY: 308
                modelWidth: 584
                modelHeight: 290
                widgetCount: 3
                actionIdsText: "n/a"
                sourceRootsText: "gameHudJson, sessionState"
                firstWidgetLabelsText: "Active, Session ID, HUD"
            }

            HomeCardSlotPreview {
                width: parent.width
                slotIndex: 4
                cardId: "relic_identity_card"
                cardType: "identity"
                cardTitleText: "RELIC Identity"
                cardSubtitleText: "Brand and visual"
                requiredCard: false
                lockedCard: false
                modelX: 798
                modelY: 10
                modelWidth: 386
                modelHeight: 588
                widgetCount: 2
                actionIdsText: "n/a"
                sourceRootsText: "renderResourcesJson"
                firstWidgetLabelsText: "Identity, Tagline"
            }
        }
    }
}
