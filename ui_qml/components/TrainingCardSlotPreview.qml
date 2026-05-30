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

    // Compatibility wrapper: DesktopCardSlotPreview contains DesignCard and ConfigTextWidget.
    DesktopCardSlotPreview {
        anchors.fill: parent
        slotLabelPrefix: "Training Slot"
        slotIndex: root.slotIndex
        cardId: root.cardId
        cardType: root.cardType
        cardTitleText: root.cardTitleText
        cardSubtitleText: root.cardSubtitleText
        requiredCard: root.requiredCard
        lockedCard: root.lockedCard
        rectText: root.rectText
        widgetCount: root.widgetCount
        actionIdsText: root.actionIdsText
        sourceRootsText: root.sourceRootsText
        firstWidgetLabelsText: root.firstWidgetLabelsText
        placeholder: root.placeholder
        roleText: root.roleText
        layoutMode: "grid"
        backgroundColor: "#111827"
        borderColor: "#334155"
        placeholderBackgroundColor: "#1F2937"
        placeholderBorderColor: "#F59E0B"
    }
}
