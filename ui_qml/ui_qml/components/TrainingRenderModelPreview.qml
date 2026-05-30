import QtQuick 2.15

Item {
    id: root

    property string pageId: "training"
    property int cardCount: 0
    property int widgetCount: 0
    property string requiredCardsText: "n/a"
    property string actionsText: "n/a"
    property string sourceRootsText: "n/a"
    property string placeholderSourcesText: "n/a"
    property string gameCanvasStatusText: "n/a"
    property bool safeStopPresent: false
    property string slotsSupportedText: "false"
    property string injectionSupportedText: "false"

    implicitWidth: 760
    implicitHeight: 420

    // Compatibility wrapper: RenderModelSummaryPreview contains DesignCard and ConfigTextWidget.
    RenderModelSummaryPreview {
        anchors.fill: parent
        previewTitle: "Training Render Model Preview"
        previewSubtitle: "TASK26F-1 bridge summary preview"
        pageId: root.pageId
        cardCount: root.cardCount
        widgetCount: root.widgetCount
        requiredCardsText: root.requiredCardsText
        actionsText: root.actionsText
        sourceRootsText: root.sourceRootsText
        placeholderSourcesText: root.placeholderSourcesText
        gameCanvasStatusText: root.gameCanvasStatusText
        safeStopPresent: root.safeStopPresent
        slotsSupportedText: root.slotsSupportedText
        injectionSupportedText: root.injectionSupportedText
        showRequiredCardsText: true
        showPlaceholderSources: true
        showGameCanvasStatus: true
        showSafeStopAndSupport: true
        useSafeStopBorder: true
        backgroundColor: "#111827"
    }
}
