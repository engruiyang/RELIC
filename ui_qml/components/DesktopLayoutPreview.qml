import QtQuick 2.15

Item {
    id: root

    property var layoutPayload: ({})
    property string previewTitle: "Desktop Layout Preview"
    property string previewSubtitle: "TASK26 real layout preview"
    property string pageId: String(layoutValue("page_id", ""))
    property real modelPageWidth: Number(layoutValue("page_width", 1200))
    property real modelPageHeight: Number(layoutValue("page_height", 800))
    property int cardCount: Number(layoutValue("card_count", 0))
    property string payloadStatusText: "n/a"
    property string payloadSourceText: "n/a"

    function layoutValue(key, fallbackValue) {
        var payload = root.layoutPayload || ({})
        if (payload[key] === undefined || payload[key] === null || payload[key] === "") {
            return fallbackValue
        }
        return payload[key]
    }

    property bool card1Visible: Boolean(layoutValue("card1_visible", false))
    property string card1Id: String(layoutValue("card1_id", ""))
    property string card1Type: String(layoutValue("card1_type", ""))
    property string card1Title: String(layoutValue("card1_title", ""))
    property string card1Subtitle: String(layoutValue("card1_subtitle", ""))
    property real card1X: Number(layoutValue("card1_x", 0))
    property real card1Y: Number(layoutValue("card1_y", 0))
    property real card1Width: Number(layoutValue("card1_width", 0))
    property real card1Height: Number(layoutValue("card1_height", 0))
    property bool card1Required: Boolean(layoutValue("card1_required", false))
    property bool card1Locked: Boolean(layoutValue("card1_locked", false))
    property int card1WidgetCount: Number(layoutValue("card1_widget_count", 0))
    property string card1ActionIdsText: String(layoutValue("card1_action_ids_text", "n/a"))
    property string card1SourceRootsText: String(layoutValue("card1_source_roots_text", "n/a"))
    property string card1FirstWidgetLabelsText: String(layoutValue("card1_first_widget_labels_text", "n/a"))
    property bool card1Placeholder: Boolean(layoutValue("card1_placeholder", false))
    property string card1RoleText: String(layoutValue("card1_role", ""))
    property bool card2Visible: Boolean(layoutValue("card2_visible", false))
    property string card2Id: String(layoutValue("card2_id", ""))
    property string card2Type: String(layoutValue("card2_type", ""))
    property string card2Title: String(layoutValue("card2_title", ""))
    property string card2Subtitle: String(layoutValue("card2_subtitle", ""))
    property real card2X: Number(layoutValue("card2_x", 0))
    property real card2Y: Number(layoutValue("card2_y", 0))
    property real card2Width: Number(layoutValue("card2_width", 0))
    property real card2Height: Number(layoutValue("card2_height", 0))
    property bool card2Required: Boolean(layoutValue("card2_required", false))
    property bool card2Locked: Boolean(layoutValue("card2_locked", false))
    property int card2WidgetCount: Number(layoutValue("card2_widget_count", 0))
    property string card2ActionIdsText: String(layoutValue("card2_action_ids_text", "n/a"))
    property string card2SourceRootsText: String(layoutValue("card2_source_roots_text", "n/a"))
    property string card2FirstWidgetLabelsText: String(layoutValue("card2_first_widget_labels_text", "n/a"))
    property bool card2Placeholder: Boolean(layoutValue("card2_placeholder", false))
    property string card2RoleText: String(layoutValue("card2_role", ""))
    property bool card3Visible: Boolean(layoutValue("card3_visible", false))
    property string card3Id: String(layoutValue("card3_id", ""))
    property string card3Type: String(layoutValue("card3_type", ""))
    property string card3Title: String(layoutValue("card3_title", ""))
    property string card3Subtitle: String(layoutValue("card3_subtitle", ""))
    property real card3X: Number(layoutValue("card3_x", 0))
    property real card3Y: Number(layoutValue("card3_y", 0))
    property real card3Width: Number(layoutValue("card3_width", 0))
    property real card3Height: Number(layoutValue("card3_height", 0))
    property bool card3Required: Boolean(layoutValue("card3_required", false))
    property bool card3Locked: Boolean(layoutValue("card3_locked", false))
    property int card3WidgetCount: Number(layoutValue("card3_widget_count", 0))
    property string card3ActionIdsText: String(layoutValue("card3_action_ids_text", "n/a"))
    property string card3SourceRootsText: String(layoutValue("card3_source_roots_text", "n/a"))
    property string card3FirstWidgetLabelsText: String(layoutValue("card3_first_widget_labels_text", "n/a"))
    property bool card3Placeholder: Boolean(layoutValue("card3_placeholder", false))
    property string card3RoleText: String(layoutValue("card3_role", ""))
    property bool card4Visible: Boolean(layoutValue("card4_visible", false))
    property string card4Id: String(layoutValue("card4_id", ""))
    property string card4Type: String(layoutValue("card4_type", ""))
    property string card4Title: String(layoutValue("card4_title", ""))
    property string card4Subtitle: String(layoutValue("card4_subtitle", ""))
    property real card4X: Number(layoutValue("card4_x", 0))
    property real card4Y: Number(layoutValue("card4_y", 0))
    property real card4Width: Number(layoutValue("card4_width", 0))
    property real card4Height: Number(layoutValue("card4_height", 0))
    property bool card4Required: Boolean(layoutValue("card4_required", false))
    property bool card4Locked: Boolean(layoutValue("card4_locked", false))
    property int card4WidgetCount: Number(layoutValue("card4_widget_count", 0))
    property string card4ActionIdsText: String(layoutValue("card4_action_ids_text", "n/a"))
    property string card4SourceRootsText: String(layoutValue("card4_source_roots_text", "n/a"))
    property string card4FirstWidgetLabelsText: String(layoutValue("card4_first_widget_labels_text", "n/a"))
    property bool card4Placeholder: Boolean(layoutValue("card4_placeholder", false))
    property string card4RoleText: String(layoutValue("card4_role", ""))
    property bool card5Visible: Boolean(layoutValue("card5_visible", false))
    property string card5Id: String(layoutValue("card5_id", ""))
    property string card5Type: String(layoutValue("card5_type", ""))
    property string card5Title: String(layoutValue("card5_title", ""))
    property string card5Subtitle: String(layoutValue("card5_subtitle", ""))
    property real card5X: Number(layoutValue("card5_x", 0))
    property real card5Y: Number(layoutValue("card5_y", 0))
    property real card5Width: Number(layoutValue("card5_width", 0))
    property real card5Height: Number(layoutValue("card5_height", 0))
    property bool card5Required: Boolean(layoutValue("card5_required", false))
    property bool card5Locked: Boolean(layoutValue("card5_locked", false))
    property int card5WidgetCount: Number(layoutValue("card5_widget_count", 0))
    property string card5ActionIdsText: String(layoutValue("card5_action_ids_text", "n/a"))
    property string card5SourceRootsText: String(layoutValue("card5_source_roots_text", "n/a"))
    property string card5FirstWidgetLabelsText: String(layoutValue("card5_first_widget_labels_text", "n/a"))
    property bool card5Placeholder: Boolean(layoutValue("card5_placeholder", false))
    property string card5RoleText: String(layoutValue("card5_role", ""))
    property bool card6Visible: Boolean(layoutValue("card6_visible", false))
    property string card6Id: String(layoutValue("card6_id", ""))
    property string card6Type: String(layoutValue("card6_type", ""))
    property string card6Title: String(layoutValue("card6_title", ""))
    property string card6Subtitle: String(layoutValue("card6_subtitle", ""))
    property real card6X: Number(layoutValue("card6_x", 0))
    property real card6Y: Number(layoutValue("card6_y", 0))
    property real card6Width: Number(layoutValue("card6_width", 0))
    property real card6Height: Number(layoutValue("card6_height", 0))
    property bool card6Required: Boolean(layoutValue("card6_required", false))
    property bool card6Locked: Boolean(layoutValue("card6_locked", false))
    property int card6WidgetCount: Number(layoutValue("card6_widget_count", 0))
    property string card6ActionIdsText: String(layoutValue("card6_action_ids_text", "n/a"))
    property string card6SourceRootsText: String(layoutValue("card6_source_roots_text", "n/a"))
    property string card6FirstWidgetLabelsText: String(layoutValue("card6_first_widget_labels_text", "n/a"))
    property bool card6Placeholder: Boolean(layoutValue("card6_placeholder", false))
    property string card6RoleText: String(layoutValue("card6_role", ""))
    property bool card7Visible: Boolean(layoutValue("card7_visible", false))
    property string card7Id: String(layoutValue("card7_id", ""))
    property string card7Type: String(layoutValue("card7_type", ""))
    property string card7Title: String(layoutValue("card7_title", ""))
    property string card7Subtitle: String(layoutValue("card7_subtitle", ""))
    property real card7X: Number(layoutValue("card7_x", 0))
    property real card7Y: Number(layoutValue("card7_y", 0))
    property real card7Width: Number(layoutValue("card7_width", 0))
    property real card7Height: Number(layoutValue("card7_height", 0))
    property bool card7Required: Boolean(layoutValue("card7_required", false))
    property bool card7Locked: Boolean(layoutValue("card7_locked", false))
    property int card7WidgetCount: Number(layoutValue("card7_widget_count", 0))
    property string card7ActionIdsText: String(layoutValue("card7_action_ids_text", "n/a"))
    property string card7SourceRootsText: String(layoutValue("card7_source_roots_text", "n/a"))
    property string card7FirstWidgetLabelsText: String(layoutValue("card7_first_widget_labels_text", "n/a"))
    property bool card7Placeholder: Boolean(layoutValue("card7_placeholder", false))
    property string card7RoleText: String(layoutValue("card7_role", ""))

    property string card1BackgroundColor: String(layoutValue("card1_background_color", ""))
    property real card1BackgroundOpacity: Number(layoutValue("card1_background_opacity", 0.92))
    property string card1BorderColor: String(layoutValue("card1_border_color", ""))
    property int card1BorderWidth: Number(layoutValue("card1_border_width", 1))
    property int card1RadiusValue: Number(layoutValue("card1_radius_value", 14))
    property string card1ShapeType: String(layoutValue("card1_shape_type", "rounded_rect"))
    property string card1BackgroundImage: String(layoutValue("card1_background_image", ""))
    property bool card1GlassEnabled: Boolean(layoutValue("card1_glass_enabled", false))
    property string card1GlassTintColor: String(layoutValue("card1_glass_tint_color", "#DDEEFF"))
    property real card1GlassOpacity: Number(layoutValue("card1_glass_opacity", 0.0))
    property bool card1GlassHighlight: Boolean(layoutValue("card1_glass_highlight", false))
    property string card2BackgroundColor: String(layoutValue("card2_background_color", ""))
    property real card2BackgroundOpacity: Number(layoutValue("card2_background_opacity", 0.92))
    property string card2BorderColor: String(layoutValue("card2_border_color", ""))
    property int card2BorderWidth: Number(layoutValue("card2_border_width", 1))
    property int card2RadiusValue: Number(layoutValue("card2_radius_value", 14))
    property string card2ShapeType: String(layoutValue("card2_shape_type", "rounded_rect"))
    property string card2BackgroundImage: String(layoutValue("card2_background_image", ""))
    property bool card2GlassEnabled: Boolean(layoutValue("card2_glass_enabled", false))
    property string card2GlassTintColor: String(layoutValue("card2_glass_tint_color", "#DDEEFF"))
    property real card2GlassOpacity: Number(layoutValue("card2_glass_opacity", 0.0))
    property bool card2GlassHighlight: Boolean(layoutValue("card2_glass_highlight", false))
    property string card3BackgroundColor: String(layoutValue("card3_background_color", ""))
    property real card3BackgroundOpacity: Number(layoutValue("card3_background_opacity", 0.92))
    property string card3BorderColor: String(layoutValue("card3_border_color", ""))
    property int card3BorderWidth: Number(layoutValue("card3_border_width", 1))
    property int card3RadiusValue: Number(layoutValue("card3_radius_value", 14))
    property string card3ShapeType: String(layoutValue("card3_shape_type", "rounded_rect"))
    property string card3BackgroundImage: String(layoutValue("card3_background_image", ""))
    property bool card3GlassEnabled: Boolean(layoutValue("card3_glass_enabled", false))
    property string card3GlassTintColor: String(layoutValue("card3_glass_tint_color", "#DDEEFF"))
    property real card3GlassOpacity: Number(layoutValue("card3_glass_opacity", 0.0))
    property bool card3GlassHighlight: Boolean(layoutValue("card3_glass_highlight", false))
    property string card4BackgroundColor: String(layoutValue("card4_background_color", ""))
    property real card4BackgroundOpacity: Number(layoutValue("card4_background_opacity", 0.92))
    property string card4BorderColor: String(layoutValue("card4_border_color", ""))
    property int card4BorderWidth: Number(layoutValue("card4_border_width", 1))
    property int card4RadiusValue: Number(layoutValue("card4_radius_value", 14))
    property string card4ShapeType: String(layoutValue("card4_shape_type", "rounded_rect"))
    property string card4BackgroundImage: String(layoutValue("card4_background_image", ""))
    property bool card4GlassEnabled: Boolean(layoutValue("card4_glass_enabled", false))
    property string card4GlassTintColor: String(layoutValue("card4_glass_tint_color", "#DDEEFF"))
    property real card4GlassOpacity: Number(layoutValue("card4_glass_opacity", 0.0))
    property bool card4GlassHighlight: Boolean(layoutValue("card4_glass_highlight", false))
    property string card5BackgroundColor: String(layoutValue("card5_background_color", ""))
    property real card5BackgroundOpacity: Number(layoutValue("card5_background_opacity", 0.92))
    property string card5BorderColor: String(layoutValue("card5_border_color", ""))
    property int card5BorderWidth: Number(layoutValue("card5_border_width", 1))
    property int card5RadiusValue: Number(layoutValue("card5_radius_value", 14))
    property string card5ShapeType: String(layoutValue("card5_shape_type", "rounded_rect"))
    property string card5BackgroundImage: String(layoutValue("card5_background_image", ""))
    property bool card5GlassEnabled: Boolean(layoutValue("card5_glass_enabled", false))
    property string card5GlassTintColor: String(layoutValue("card5_glass_tint_color", "#DDEEFF"))
    property real card5GlassOpacity: Number(layoutValue("card5_glass_opacity", 0.0))
    property bool card5GlassHighlight: Boolean(layoutValue("card5_glass_highlight", false))
    property string card6BackgroundColor: String(layoutValue("card6_background_color", ""))
    property real card6BackgroundOpacity: Number(layoutValue("card6_background_opacity", 0.92))
    property string card6BorderColor: String(layoutValue("card6_border_color", ""))
    property int card6BorderWidth: Number(layoutValue("card6_border_width", 1))
    property int card6RadiusValue: Number(layoutValue("card6_radius_value", 14))
    property string card6ShapeType: String(layoutValue("card6_shape_type", "rounded_rect"))
    property string card6BackgroundImage: String(layoutValue("card6_background_image", ""))
    property bool card6GlassEnabled: Boolean(layoutValue("card6_glass_enabled", false))
    property string card6GlassTintColor: String(layoutValue("card6_glass_tint_color", "#DDEEFF"))
    property real card6GlassOpacity: Number(layoutValue("card6_glass_opacity", 0.0))
    property bool card6GlassHighlight: Boolean(layoutValue("card6_glass_highlight", false))
    property string card7BackgroundColor: String(layoutValue("card7_background_color", ""))
    property real card7BackgroundOpacity: Number(layoutValue("card7_background_opacity", 0.92))
    property string card7BorderColor: String(layoutValue("card7_border_color", ""))
    property int card7BorderWidth: Number(layoutValue("card7_border_width", 1))
    property int card7RadiusValue: Number(layoutValue("card7_radius_value", 14))
    property string card7ShapeType: String(layoutValue("card7_shape_type", "rounded_rect"))
    property string card7BackgroundImage: String(layoutValue("card7_background_image", ""))
    property bool card7GlassEnabled: Boolean(layoutValue("card7_glass_enabled", false))
    property string card7GlassTintColor: String(layoutValue("card7_glass_tint_color", "#DDEEFF"))
    property real card7GlassOpacity: Number(layoutValue("card7_glass_opacity", 0.0))
    property bool card7GlassHighlight: Boolean(layoutValue("card7_glass_highlight", false))

    readonly property real canvasScale: Math.max(
        0.05,
        Math.min(
            (layoutCanvas.width - 8) / Math.max(1, modelPageWidth),
            (layoutCanvas.height - 8) / Math.max(1, modelPageHeight)
        )
    )

    implicitWidth: 760
    implicitHeight: 560

    DesignCard {
        anchors.fill: parent
        cardTitle: root.previewTitle
        cardSubtitle: root.previewSubtitle
        backgroundColor: "#101722"
        borderColor: "#345175"
        radiusValue: 18
        paddingValue: 12
        glassEnabled: true
        glassTintColor: "#BFDFFF"
        glassOpacity: 0.06
        glassHighlight: true

        Column {
            width: parent.width
            spacing: 8

            Row {
                width: parent.width
                spacing: 8

                ConfigTextWidget {
                    width: 140
                    label: "Page"
                    value: root.pageId.length > 0 ? root.pageId : "n/a"
                }

                ConfigTextWidget {
                    width: 140
                    label: "Cards"
                    value: String(root.cardCount)
                }

                ConfigTextWidget {
                    width: 180
                    label: "Payload"
                    value: root.payloadStatusText
                }

                ConfigTextWidget {
                    width: Math.max(160, parent.width - 500)
                    label: "Source"
                    value: root.payloadSourceText
                }
            }

            Rectangle {
                id: layoutCanvas
                width: parent.width
                height: Math.max(360, root.height - 112)
                color: "#070B12"
                radius: 14
                border.color: "#24364F"
                border.width: 1
                clip: true

                Rectangle {
                    x: 4
                    y: 4
                    width: Math.max(1, root.modelPageWidth * root.canvasScale)
                    height: Math.max(1, root.modelPageHeight * root.canvasScale)
                    color: "#0D1420"
                    border.color: "#36506F"
                    border.width: 1
                    radius: 10
                }

                DesktopLayoutCardPreview {
                    cardVisible: root.card1Visible
                    cardId: root.card1Id
                    cardType: root.card1Type
                    cardTitleText: root.card1Title
                    cardSubtitleText: root.card1Subtitle
                    modelX: root.card1X
                    modelY: root.card1Y
                    modelWidth: root.card1Width
                    modelHeight: root.card1Height
                    previewScale: root.canvasScale
                    requiredCard: root.card1Required
                    lockedCard: root.card1Locked
                    widgetCount: root.card1WidgetCount
                    actionIdsText: root.card1ActionIdsText
                    sourceRootsText: root.card1SourceRootsText
                    firstWidgetLabelsText: root.card1FirstWidgetLabelsText
                    placeholder: root.card1Placeholder
                    roleText: root.card1RoleText
                cardBackgroundColor: root.card1BackgroundColor
                cardBackgroundOpacity: root.card1BackgroundOpacity
                cardBorderColor: root.card1BorderColor
                cardBorderWidth: root.card1BorderWidth
                cardRadiusValue: root.card1RadiusValue
                cardShapeType: root.card1ShapeType
                cardBackgroundImage: root.card1BackgroundImage
                cardGlassEnabled: root.card1GlassEnabled
                cardGlassTintColor: root.card1GlassTintColor
                cardGlassOpacity: root.card1GlassOpacity
                cardGlassHighlight: root.card1GlassHighlight
                }
                DesktopLayoutCardPreview {
                    cardVisible: root.card2Visible
                    cardId: root.card2Id
                    cardType: root.card2Type
                    cardTitleText: root.card2Title
                    cardSubtitleText: root.card2Subtitle
                    modelX: root.card2X
                    modelY: root.card2Y
                    modelWidth: root.card2Width
                    modelHeight: root.card2Height
                    previewScale: root.canvasScale
                    requiredCard: root.card2Required
                    lockedCard: root.card2Locked
                    widgetCount: root.card2WidgetCount
                    actionIdsText: root.card2ActionIdsText
                    sourceRootsText: root.card2SourceRootsText
                    firstWidgetLabelsText: root.card2FirstWidgetLabelsText
                    placeholder: root.card2Placeholder
                    roleText: root.card2RoleText
                cardBackgroundColor: root.card2BackgroundColor
                cardBackgroundOpacity: root.card2BackgroundOpacity
                cardBorderColor: root.card2BorderColor
                cardBorderWidth: root.card2BorderWidth
                cardRadiusValue: root.card2RadiusValue
                cardShapeType: root.card2ShapeType
                cardBackgroundImage: root.card2BackgroundImage
                cardGlassEnabled: root.card2GlassEnabled
                cardGlassTintColor: root.card2GlassTintColor
                cardGlassOpacity: root.card2GlassOpacity
                cardGlassHighlight: root.card2GlassHighlight
                }
                DesktopLayoutCardPreview {
                    cardVisible: root.card3Visible
                    cardId: root.card3Id
                    cardType: root.card3Type
                    cardTitleText: root.card3Title
                    cardSubtitleText: root.card3Subtitle
                    modelX: root.card3X
                    modelY: root.card3Y
                    modelWidth: root.card3Width
                    modelHeight: root.card3Height
                    previewScale: root.canvasScale
                    requiredCard: root.card3Required
                    lockedCard: root.card3Locked
                    widgetCount: root.card3WidgetCount
                    actionIdsText: root.card3ActionIdsText
                    sourceRootsText: root.card3SourceRootsText
                    firstWidgetLabelsText: root.card3FirstWidgetLabelsText
                    placeholder: root.card3Placeholder
                    roleText: root.card3RoleText
                cardBackgroundColor: root.card3BackgroundColor
                cardBackgroundOpacity: root.card3BackgroundOpacity
                cardBorderColor: root.card3BorderColor
                cardBorderWidth: root.card3BorderWidth
                cardRadiusValue: root.card3RadiusValue
                cardShapeType: root.card3ShapeType
                cardBackgroundImage: root.card3BackgroundImage
                cardGlassEnabled: root.card3GlassEnabled
                cardGlassTintColor: root.card3GlassTintColor
                cardGlassOpacity: root.card3GlassOpacity
                cardGlassHighlight: root.card3GlassHighlight
                }
                DesktopLayoutCardPreview {
                    cardVisible: root.card4Visible
                    cardId: root.card4Id
                    cardType: root.card4Type
                    cardTitleText: root.card4Title
                    cardSubtitleText: root.card4Subtitle
                    modelX: root.card4X
                    modelY: root.card4Y
                    modelWidth: root.card4Width
                    modelHeight: root.card4Height
                    previewScale: root.canvasScale
                    requiredCard: root.card4Required
                    lockedCard: root.card4Locked
                    widgetCount: root.card4WidgetCount
                    actionIdsText: root.card4ActionIdsText
                    sourceRootsText: root.card4SourceRootsText
                    firstWidgetLabelsText: root.card4FirstWidgetLabelsText
                    placeholder: root.card4Placeholder
                    roleText: root.card4RoleText
                cardBackgroundColor: root.card4BackgroundColor
                cardBackgroundOpacity: root.card4BackgroundOpacity
                cardBorderColor: root.card4BorderColor
                cardBorderWidth: root.card4BorderWidth
                cardRadiusValue: root.card4RadiusValue
                cardShapeType: root.card4ShapeType
                cardBackgroundImage: root.card4BackgroundImage
                cardGlassEnabled: root.card4GlassEnabled
                cardGlassTintColor: root.card4GlassTintColor
                cardGlassOpacity: root.card4GlassOpacity
                cardGlassHighlight: root.card4GlassHighlight
                }
                DesktopLayoutCardPreview {
                    cardVisible: root.card5Visible
                    cardId: root.card5Id
                    cardType: root.card5Type
                    cardTitleText: root.card5Title
                    cardSubtitleText: root.card5Subtitle
                    modelX: root.card5X
                    modelY: root.card5Y
                    modelWidth: root.card5Width
                    modelHeight: root.card5Height
                    previewScale: root.canvasScale
                    requiredCard: root.card5Required
                    lockedCard: root.card5Locked
                    widgetCount: root.card5WidgetCount
                    actionIdsText: root.card5ActionIdsText
                    sourceRootsText: root.card5SourceRootsText
                    firstWidgetLabelsText: root.card5FirstWidgetLabelsText
                    placeholder: root.card5Placeholder
                    roleText: root.card5RoleText
                cardBackgroundColor: root.card5BackgroundColor
                cardBackgroundOpacity: root.card5BackgroundOpacity
                cardBorderColor: root.card5BorderColor
                cardBorderWidth: root.card5BorderWidth
                cardRadiusValue: root.card5RadiusValue
                cardShapeType: root.card5ShapeType
                cardBackgroundImage: root.card5BackgroundImage
                cardGlassEnabled: root.card5GlassEnabled
                cardGlassTintColor: root.card5GlassTintColor
                cardGlassOpacity: root.card5GlassOpacity
                cardGlassHighlight: root.card5GlassHighlight
                }
                DesktopLayoutCardPreview {
                    cardVisible: root.card6Visible
                    cardId: root.card6Id
                    cardType: root.card6Type
                    cardTitleText: root.card6Title
                    cardSubtitleText: root.card6Subtitle
                    modelX: root.card6X
                    modelY: root.card6Y
                    modelWidth: root.card6Width
                    modelHeight: root.card6Height
                    previewScale: root.canvasScale
                    requiredCard: root.card6Required
                    lockedCard: root.card6Locked
                    widgetCount: root.card6WidgetCount
                    actionIdsText: root.card6ActionIdsText
                    sourceRootsText: root.card6SourceRootsText
                    firstWidgetLabelsText: root.card6FirstWidgetLabelsText
                    placeholder: root.card6Placeholder
                    roleText: root.card6RoleText
                cardBackgroundColor: root.card6BackgroundColor
                cardBackgroundOpacity: root.card6BackgroundOpacity
                cardBorderColor: root.card6BorderColor
                cardBorderWidth: root.card6BorderWidth
                cardRadiusValue: root.card6RadiusValue
                cardShapeType: root.card6ShapeType
                cardBackgroundImage: root.card6BackgroundImage
                cardGlassEnabled: root.card6GlassEnabled
                cardGlassTintColor: root.card6GlassTintColor
                cardGlassOpacity: root.card6GlassOpacity
                cardGlassHighlight: root.card6GlassHighlight
                }
                DesktopLayoutCardPreview {
                    cardVisible: root.card7Visible
                    cardId: root.card7Id
                    cardType: root.card7Type
                    cardTitleText: root.card7Title
                    cardSubtitleText: root.card7Subtitle
                    modelX: root.card7X
                    modelY: root.card7Y
                    modelWidth: root.card7Width
                    modelHeight: root.card7Height
                    previewScale: root.canvasScale
                    requiredCard: root.card7Required
                    lockedCard: root.card7Locked
                    widgetCount: root.card7WidgetCount
                    actionIdsText: root.card7ActionIdsText
                    sourceRootsText: root.card7SourceRootsText
                    firstWidgetLabelsText: root.card7FirstWidgetLabelsText
                    placeholder: root.card7Placeholder
                    roleText: root.card7RoleText
                cardBackgroundColor: root.card7BackgroundColor
                cardBackgroundOpacity: root.card7BackgroundOpacity
                cardBorderColor: root.card7BorderColor
                cardBorderWidth: root.card7BorderWidth
                cardRadiusValue: root.card7RadiusValue
                cardShapeType: root.card7ShapeType
                cardBackgroundImage: root.card7BackgroundImage
                cardGlassEnabled: root.card7GlassEnabled
                cardGlassTintColor: root.card7GlassTintColor
                cardGlassOpacity: root.card7GlassOpacity
                cardGlassHighlight: root.card7GlassHighlight
                }
            }
        }
    }
}
