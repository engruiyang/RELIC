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

    // Compatibility wrapper: DesktopCardSlotPreview contains DesignCard and ConfigTextWidget.
    DesktopCardSlotPreview {
        anchors.fill: parent
        slotLabelPrefix: "Slot"
        slotIndex: root.slotIndex
        cardId: root.cardId
        cardType: root.cardType
        cardTitleText: root.cardTitleText
        cardSubtitleText: root.cardSubtitleText
        requiredCard: root.requiredCard
        lockedCard: root.lockedCard
        rectText: "x=" + root.modelX + ", y=" + root.modelY + ", w=" + root.modelWidth + ", h=" + root.modelHeight
        widgetCount: root.widgetCount
        actionIdsText: root.actionIdsText
        sourceRootsText: root.sourceRootsText
        firstWidgetLabelsText: root.firstWidgetLabelsText
        placeholder: false
        roleText: ""
        layoutMode: "stack"
        backgroundColor: "#121B27"
        borderColor: "#35516F"
    }
}
