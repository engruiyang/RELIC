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

    // Compatibility wrapper: RenderModelSummaryPreview contains DesignCard and ConfigTextWidget.
    RenderModelSummaryPreview {
        anchors.fill: parent
        previewTitle: "Home Render Model Preview"
        previewSubtitle: "TASK26E-1 summary-only preview"
        pageId: root.pageId
        cardCount: root.cardCount
        widgetCount: root.widgetCount
        requiredCardCount: root.requiredCardCount
        lockedCardCount: root.lockedCardCount
        actionsText: root.actionsText
        sourceRootsText: root.sourceRootsText
        cardIdsText: root.cardIdsText
        showRequiredLockedCounts: true
        showCardIds: true
        backgroundColor: "#111A25"
        borderColor: "#3B5674"
    }
}
