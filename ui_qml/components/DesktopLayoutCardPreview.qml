import QtQuick 2.15

Item {
    id: root

    property var guiBridge: null
    property var appStateObj: ({})
    property var runtimeSnapshotObj: ({})
    property var sessionStateObj: ({})
    property var controlStateObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})
    property var renderResourcesObj: ({})

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

    property string widget1Type: ""
    property string widget1Id: ""
    property string widget1Label: ""
    property string widget1Source: ""
    property string widget1Fallback: ""
    property string widget1Unit: ""
    property string widget1ActionId: ""
    property string widget1Variant: ""
    property bool widget1Required: false
    property string widget1Value: ""

    property string widget2Type: ""
    property string widget2Id: ""
    property string widget2Label: ""
    property string widget2Source: ""
    property string widget2Fallback: ""
    property string widget2Unit: ""
    property string widget2ActionId: ""
    property string widget2Variant: ""
    property bool widget2Required: false
    property string widget2Value: ""

    property string widget3Type: ""
    property string widget3Id: ""
    property string widget3Label: ""
    property string widget3Source: ""
    property string widget3Fallback: ""
    property string widget3Unit: ""
    property string widget3ActionId: ""
    property string widget3Variant: ""
    property bool widget3Required: false
    property string widget3Value: ""

    property string widget4Type: ""
    property string widget4Id: ""
    property string widget4Label: ""
    property string widget4Source: ""
    property string widget4Fallback: ""
    property string widget4Unit: ""
    property string widget4ActionId: ""
    property string widget4Variant: ""
    property bool widget4Required: false
    property string widget4Value: ""

    property string widget5Type: ""
    property string widget5Id: ""
    property string widget5Label: ""
    property string widget5Source: ""
    property string widget5Fallback: ""
    property string widget5Unit: ""
    property string widget5ActionId: ""
    property string widget5Variant: ""
    property bool widget5Required: false
    property string widget5Value: ""

    property string widget6Type: ""
    property string widget6Id: ""
    property string widget6Label: ""
    property string widget6Source: ""
    property string widget6Fallback: ""
    property string widget6Unit: ""
    property string widget6ActionId: ""
    property string widget6Variant: ""
    property bool widget6Required: false
    property string widget6Value: ""

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

    function safeText(value, fallbackValue) {
        var fallbackText = (fallbackValue === undefined || fallbackValue === null || fallbackValue === "") ? "n/a" : String(fallbackValue)
        if (value === undefined || value === null || value === "") {
            return fallbackText
        }
        return String(value)
    }

    function sourceValue(source, fallbackValue) {
        if (!source || source === "") return fallbackValue

        if (source === "appState.user_note") return safeText(root.appStateObj && root.appStateObj.user_note, fallbackValue)
        if (source === "appState.report_note") return safeText(root.appStateObj && root.appStateObj.report_note, fallbackValue)

        if (source === "runtimeSnapshot.connection_status") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.connection_status, fallbackValue)
        if (source === "runtimeSnapshot.stream_alive") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.stream_alive, fallbackValue)
        if (source === "runtimeSnapshot.attention") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.attention, fallbackValue)
        if (source === "runtimeSnapshot.attention_age_ms") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.attention_age_ms, fallbackValue)
        if (source === "runtimeSnapshot.gyro_x") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.gyro_x, fallbackValue)
        if (source === "runtimeSnapshot.gyro_y") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.gyro_y, fallbackValue)
        if (source === "runtimeSnapshot.gyro_z") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.gyro_z, fallbackValue)
        if (source === "runtimeSnapshot.gyro_age_ms") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.gyro_age_ms, fallbackValue)
        if (source === "runtimeSnapshot.warning_flags") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.warning_flags, fallbackValue)
        if (source === "runtimeSnapshot.error_flags") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.error_flags, fallbackValue)
        if (source === "runtimeSnapshot.sqi") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.sqi, fallbackValue)
        if (source === "runtimeSnapshot.fi") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.fi, fallbackValue)
        if (source === "runtimeSnapshot.control_state") return safeText(root.runtimeSnapshotObj && root.runtimeSnapshotObj.control_state, fallbackValue)

        if (source === "sessionState.session_active") return safeText(root.sessionStateObj && root.sessionStateObj.session_active, fallbackValue)
        if (source === "sessionState.current_session_id") return safeText(root.sessionStateObj && root.sessionStateObj.current_session_id, fallbackValue)
        if (source === "sessionState.session_elapsed_ms") return safeText(root.sessionStateObj && root.sessionStateObj.session_elapsed_ms, fallbackValue)
        if (source === "sessionState.session_count") return safeText(root.sessionStateObj && root.sessionStateObj.session_count, fallbackValue)
        if (source === "sessionState.latest_report_path") return safeText(root.sessionStateObj && root.sessionStateObj.latest_report_path, fallbackValue)
        if (source === "sessionState.report_path") return safeText(root.sessionStateObj && root.sessionStateObj.report_path, fallbackValue)
        if (source === "sessionState.status") return safeText(root.sessionStateObj && root.sessionStateObj.status, fallbackValue)

        if (source === "controlState.current_user_id") return safeText(root.controlStateObj && root.controlStateObj.current_user_id, fallbackValue)
        if (source === "controlState.calibration_usable") return safeText(root.controlStateObj && root.controlStateObj.calibration_usable, fallbackValue)
        if (source === "controlState.last_calibration_id") return safeText(root.controlStateObj && root.controlStateObj.last_calibration_id, fallbackValue)
        if (source === "controlStateJson.current_user_id") return safeText(root.controlStateObj && root.controlStateObj.current_user_id, fallbackValue)
        if (source === "controlStateJson.profile_loaded") return safeText(root.controlStateObj && root.controlStateObj.profile_loaded, fallbackValue)
        if (source === "controlStateJson.last_calibration_id") return safeText(root.controlStateObj && root.controlStateObj.last_calibration_id, fallbackValue)
        if (source === "controlStateJson.calibration_usable") return safeText(root.controlStateObj && root.controlStateObj.calibration_usable, fallbackValue)
        if (source === "controlStateJson.calibration_status") return safeText(root.controlStateObj && root.controlStateObj.calibration_status, fallbackValue)
        if (source === "controlStateJson.attention_low_threshold") return safeText(root.controlStateObj && root.controlStateObj.attention_low_threshold, fallbackValue)
        if (source === "controlStateJson.attention_high_threshold") return safeText(root.controlStateObj && root.controlStateObj.attention_high_threshold, fallbackValue)
        if (source === "controlStateJson.preferred_game_id") return safeText(root.controlStateObj && root.controlStateObj.preferred_game_id, fallbackValue)
        if (source === "controlStateJson.attention_baseline") return safeText(root.controlStateObj && root.controlStateObj.attention_baseline, fallbackValue)
        if (source === "controlStateJson.gyro_noise_rms") return safeText(root.controlStateObj && root.controlStateObj.gyro_noise_rms, fallbackValue)
        if (source === "controlStateJson.calibration_progress_status") return safeText(root.controlStateObj && root.controlStateObj.calibration_progress_status, fallbackValue)
        if (source === "controlStateJson.calibration_progress_phase") return safeText(root.controlStateObj && root.controlStateObj.calibration_progress_phase, fallbackValue)
        if (source === "controlStateJson.calibration_operator_guidance") return safeText(root.controlStateObj && root.controlStateObj.calibration_operator_guidance, fallbackValue)
        if (source === "controlStateJson.last_command") return safeText(root.controlStateObj && root.controlStateObj.last_command, fallbackValue)

        if (source === "gameHudJson") return safeText(root.gameHudObj, fallbackValue)
        if (source === "gameHudJson.status") return safeText(root.gameHudObj && root.gameHudObj.status, fallbackValue)
        if (source === "gameHudJson.score") return safeText(root.gameHudObj && root.gameHudObj.score, fallbackValue)
        if (source === "gameHudJson.focus_index") return safeText(root.gameHudObj && root.gameHudObj.focus_index, fallbackValue)
        if (source === "gameViewJson.game_id") return safeText(root.gameViewObj && root.gameViewObj.game_id, fallbackValue)

        if (source === "renderResourcesJson.task26_user_layout_status") return safeText(root.renderResourcesObj && root.renderResourcesObj.task26_user_layout_status, fallbackValue)
        if (source === "renderResourcesJson.assets.ui.logo.main") return safeText(root.renderResourcesObj && root.renderResourcesObj.task25_logo_main_path, fallbackValue)

        return fallbackValue
    }

    function widgetDisplayText(type, label, source, fallback, unit, value) {
        var typeText = safeText(type, "unknown")
        var labelText = safeText(label, typeText)
        var resolved = value && value.length > 0 ? value : sourceValue(source, fallback)
        var unitText = unit && unit.length > 0 ? " " + unit : ""
        if (type === "text") return labelText + ": " + safeText(resolved, fallback)
        if (type === "metric") return labelText + ": " + safeText(resolved, fallback) + unitText
        if (type === "hud") return labelText + ": " + safeText(resolved, fallback)
        if (type === "image") return labelText + " · image source: " + safeText(source, fallback)
        if (type === "game_placeholder") return "GameCanvas Placeholder · " + safeText(root.roleText, safeText(resolved, fallback))
        if (type === "button") return labelText + " · " + safeText(source, fallback)
        return labelText + " (" + typeText + "): " + safeText(resolved, fallback)
    }

    function widgetVisible(type, idx) {
        return idx <= root.widgetCount && type.length > 0
    }

    function buttonLabel(label, actionId, required) {
        var base = label && label.length > 0 ? label : actionId
        if (required) return base + " *"
        return base
    }

    function invokeDesktopAction(actionId) {
        if (!actionId || actionId.length === 0) {
            return ""
        }
        if (!root.guiBridge || !root.guiBridge.invokeAction) {
            return ""
        }
        return root.guiBridge.invokeAction(actionId, "{}")
    }

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

            ConfigTextWidget { width: parent.width; label: "Type"; value: root.cardType.length > 0 ? root.cardType : "n/a" }
            ConfigTextWidget { width: parent.width; label: "Widgets"; value: String(root.widgetCount) }
            ConfigTextWidget { width: parent.width; visible: root.placeholder || root.roleText.length > 0; label: "Role"; value: root.roleText.length > 0 ? root.roleText : "n/a" }

            Item {
                width: parent.width
                height: widgetVisible(root.widget1Type, 1) ? (root.widget1Type === "button" ? 62 : 24) : 0
                visible: widgetVisible(root.widget1Type, 1)
                ConfigButtonWidget { width: parent.width; buttonWidth: parent.width; visible: root.widget1Type === "button"; guiBridge: null; label: buttonLabel(root.widget1Label, root.widget1ActionId, root.widget1Required); actionId: root.widget1ActionId; variant: root.widget1Variant; required: root.widget1Required; onActionRequested: root.invokeDesktopAction(actionId) }
                ConfigTextWidget { width: parent.width; visible: root.widget1Type !== "button"; label: root.widget1Id; value: root.widgetDisplayText(root.widget1Type, root.widget1Label, root.widget1Source, root.widget1Fallback, root.widget1Unit, root.widget1Value) }
                ConfigTextWidget { y: 40; width: parent.width; visible: root.widget1Type === "button"; label: "Action"; value: root.widget1ActionId + " · " + root.widget1Variant }
            }
            Item {
                width: parent.width
                height: widgetVisible(root.widget2Type, 2) ? (root.widget2Type === "button" ? 62 : 24) : 0
                visible: widgetVisible(root.widget2Type, 2)
                ConfigButtonWidget { width: parent.width; buttonWidth: parent.width; visible: root.widget2Type === "button"; guiBridge: null; label: buttonLabel(root.widget2Label, root.widget2ActionId, root.widget2Required); actionId: root.widget2ActionId; variant: root.widget2Variant; required: root.widget2Required; onActionRequested: root.invokeDesktopAction(actionId) }
                ConfigTextWidget { width: parent.width; visible: root.widget2Type !== "button"; label: root.widget2Id; value: root.widgetDisplayText(root.widget2Type, root.widget2Label, root.widget2Source, root.widget2Fallback, root.widget2Unit, root.widget2Value) }
                ConfigTextWidget { y: 40; width: parent.width; visible: root.widget2Type === "button"; label: "Action"; value: root.widget2ActionId + " · " + root.widget2Variant }
            }
            Item {
                width: parent.width
                height: widgetVisible(root.widget3Type, 3) ? (root.widget3Type === "button" ? 62 : 24) : 0
                visible: widgetVisible(root.widget3Type, 3)
                ConfigButtonWidget { width: parent.width; buttonWidth: parent.width; visible: root.widget3Type === "button"; guiBridge: null; label: buttonLabel(root.widget3Label, root.widget3ActionId, root.widget3Required); actionId: root.widget3ActionId; variant: root.widget3Variant; required: root.widget3Required; onActionRequested: root.invokeDesktopAction(actionId) }
                ConfigTextWidget { width: parent.width; visible: root.widget3Type !== "button"; label: root.widget3Id; value: root.widgetDisplayText(root.widget3Type, root.widget3Label, root.widget3Source, root.widget3Fallback, root.widget3Unit, root.widget3Value) }
                ConfigTextWidget { y: 40; width: parent.width; visible: root.widget3Type === "button"; label: "Action"; value: root.widget3ActionId + " · " + root.widget3Variant }
            }
            Item {
                width: parent.width
                height: widgetVisible(root.widget4Type, 4) ? (root.widget4Type === "button" ? 62 : 24) : 0
                visible: widgetVisible(root.widget4Type, 4)
                ConfigButtonWidget { width: parent.width; buttonWidth: parent.width; visible: root.widget4Type === "button"; guiBridge: null; label: buttonLabel(root.widget4Label, root.widget4ActionId, root.widget4Required); actionId: root.widget4ActionId; variant: root.widget4Variant; required: root.widget4Required; onActionRequested: root.invokeDesktopAction(actionId) }
                ConfigTextWidget { width: parent.width; visible: root.widget4Type !== "button"; label: root.widget4Id; value: root.widgetDisplayText(root.widget4Type, root.widget4Label, root.widget4Source, root.widget4Fallback, root.widget4Unit, root.widget4Value) }
                ConfigTextWidget { y: 40; width: parent.width; visible: root.widget4Type === "button"; label: "Action"; value: root.widget4ActionId + " · " + root.widget4Variant }
            }
            Item {
                width: parent.width
                height: widgetVisible(root.widget5Type, 5) ? (root.widget5Type === "button" ? 62 : 24) : 0
                visible: widgetVisible(root.widget5Type, 5)
                ConfigButtonWidget { width: parent.width; buttonWidth: parent.width; visible: root.widget5Type === "button"; guiBridge: null; label: buttonLabel(root.widget5Label, root.widget5ActionId, root.widget5Required); actionId: root.widget5ActionId; variant: root.widget5Variant; required: root.widget5Required; onActionRequested: root.invokeDesktopAction(actionId) }
                ConfigTextWidget { width: parent.width; visible: root.widget5Type !== "button"; label: root.widget5Id; value: root.widgetDisplayText(root.widget5Type, root.widget5Label, root.widget5Source, root.widget5Fallback, root.widget5Unit, root.widget5Value) }
                ConfigTextWidget { y: 40; width: parent.width; visible: root.widget5Type === "button"; label: "Action"; value: root.widget5ActionId + " · " + root.widget5Variant }
            }
            Item {
                width: parent.width
                height: widgetVisible(root.widget6Type, 6) ? (root.widget6Type === "button" ? 62 : 24) : 0
                visible: widgetVisible(root.widget6Type, 6)
                ConfigButtonWidget { width: parent.width; buttonWidth: parent.width; visible: root.widget6Type === "button"; guiBridge: null; label: buttonLabel(root.widget6Label, root.widget6ActionId, root.widget6Required); actionId: root.widget6ActionId; variant: root.widget6Variant; required: root.widget6Required; onActionRequested: root.invokeDesktopAction(actionId) }
                ConfigTextWidget { width: parent.width; visible: root.widget6Type !== "button"; label: root.widget6Id; value: root.widgetDisplayText(root.widget6Type, root.widget6Label, root.widget6Source, root.widget6Fallback, root.widget6Unit, root.widget6Value) }
                ConfigTextWidget { y: 40; width: parent.width; visible: root.widget6Type === "button"; label: "Action"; value: root.widget6ActionId + " · " + root.widget6Variant }
            }
        }
    }
}
