import QtQuick 2.15

Item {
    id: root

    property string cardId: ""
    property string cardType: ""
    property string cardTitleText: ""
    property string cardSubtitleText: ""
    property real modelX: 0
    property real modelY: 0
    property real modelWidth: 0
    property real modelHeight: 0
    property real previewScale: 1.0
    property bool requiredCard: false
    property bool lockedCard: false
    property int widgetCount: 0
    property string actionIdsText: "n/a"
    property string sourceRootsText: "n/a"
    property string firstWidgetLabelsText: "n/a"
    property bool placeholder: false
    property string roleText: ""
    property bool cardVisible: true

    property string cardBackgroundColor: ""
    property real cardBackgroundOpacity: 0.92
    property string cardBorderColor: ""
    property int cardBorderWidth: 1
    property int cardRadiusValue: 14
    property string cardShapeType: "rounded_rect"
    property string cardBackgroundImage: ""
    property bool cardGlassEnabled: false
    property string cardGlassTintColor: "#DDEEFF"
    property real cardGlassOpacity: 0.0
    property bool cardGlassHighlight: false

    x: Math.round(modelX * previewScale)
    y: Math.round(modelY * previewScale)
    width: Math.max(96, Math.round(modelWidth * previewScale))
    height: Math.max(78, Math.round(modelHeight * previewScale))
    visible: cardVisible && cardId.length > 0

    DesignCard {
        anchors.fill: parent
        cardTitle: root.cardId
        cardSubtitle: root.cardTitleText.length > 0 ? root.cardTitleText : root.cardType
        backgroundColor: root.cardBackgroundColor.length > 0
            ? root.cardBackgroundColor
            : (root.placeholder ? "#2A2337" : "#151B24")
        backgroundOpacity: root.cardBackgroundOpacity
        backgroundImage: root.cardBackgroundImage
        borderColor: root.cardBorderColor.length > 0
            ? root.cardBorderColor
            : (root.requiredCard ? "#5D8CFF" : "#2B3A4C")
        borderWidth: root.lockedCard ? Math.max(2, root.cardBorderWidth) : root.cardBorderWidth
        radiusValue: root.cardRadiusValue
        shapeType: root.cardShapeType
        paddingValue: 10
        glassEnabled: root.cardGlassEnabled
        glassTintColor: root.cardGlassTintColor
        glassOpacity: root.cardGlassOpacity
        glassHighlight: root.cardGlassHighlight

        Column {
            width: parent.width
            spacing: 4

            ConfigTextWidget {
                width: parent.width
                label: "Type"
                value: root.cardType.length > 0 ? root.cardType : "n/a"
            }

            ConfigTextWidget {
                width: parent.width
                label: "Rect"
                value: "x=" + Math.round(root.modelX) + ", y=" + Math.round(root.modelY)
                    + ", w=" + Math.round(root.modelWidth) + ", h=" + Math.round(root.modelHeight)
            }

            ConfigTextWidget {
                width: parent.width
                label: "Widgets"
                value: String(root.widgetCount)
            }

            ConfigTextWidget {
                width: parent.width
                label: "Actions"
                value: root.actionIdsText
            }

            ConfigTextWidget {
                width: parent.width
                label: "Sources"
                value: root.sourceRootsText
            }

            ConfigTextWidget {
                width: parent.width
                label: "First Widgets"
                value: root.firstWidgetLabelsText
            }

            ConfigTextWidget {
                width: parent.width
                label: "Style"
                value: root.cardShapeType
                    + " / opacity=" + Number(root.cardBackgroundOpacity).toFixed(2)
                    + " / glass=" + String(root.cardGlassEnabled)
            }

            ConfigTextWidget {
                width: parent.width
                visible: root.placeholder || root.roleText.length > 0
                label: "Role"
                value: root.roleText.length > 0 ? root.roleText : "n/a"
            }
        }
    }
}
