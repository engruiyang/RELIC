import QtQuick 2.15

Item {
    id: root

    property var layoutPayload: ({})
    property var guiBridge: null
    property var appStateObj: ({})
    property var runtimeSnapshotObj: ({})
    property var sessionStateObj: ({})
    property var controlStateObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})
    property var renderResourcesObj: ({})
    property var designThemeObj: ({})
    property var gameStyleObj: ({})
    property var effectStyleObj: ({})
    property string previewTitle: "Desktop Layout Preview"
    property string previewSubtitle: "TASK26 real layout preview"
    property string pageId: String(layoutValue("page_id", ""))
    property real modelPageWidth: Number(layoutValue("page_width", 1200))
    property real modelPageHeight: Number(layoutValue("page_height", 800))
    property int cardCount: Number(layoutValue("card_count", 0))
    property string payloadStatusText: "n/a"
    property string payloadSourceText: "n/a"
    property string sharedReportActionRaw: ""
    property string sharedSelectedReportSessionId: ""
    property string currentUserIdText: String((root.controlStateObj && root.controlStateObj.current_user_id) || (root.appStateObj && root.appStateObj.current_user_id) || "")

    onCurrentUserIdTextChanged: {
        // Prevent report cards from displaying paths/previews returned for a previously loaded user.
        root.sharedReportActionRaw = ""
        root.sharedSelectedReportSessionId = ""
    }

    function validReportSessionId(value) {
        var text = String(value === undefined || value === null ? "" : value).trim()
        return text.length > 0 && text !== "n/a" && text !== "no_report_available" && text !== "manual" && text !== "null"
    }

    function reportSessionIdFromActionRaw(raw) {
        try {
            var obj = JSON.parse(raw || "{}")
            var result = (obj.result && typeof obj.result === "object") ? obj.result : ({})
            var detail = (obj.detail && typeof obj.detail === "object") ? obj.detail : ({})
            var report = (obj.report && typeof obj.report === "object") ? obj.report : ({})
            var resultDetail = (result.detail && typeof result.detail === "object") ? result.detail : ({})
            var resultReport = (result.report && typeof result.report === "object") ? result.report : ({})
            var candidates = [
                obj.session_id, result.session_id, detail.session_id, report.session_id,
                resultDetail.session_id, resultReport.session_id,
                obj.latest_session_id, result.latest_session_id
            ]
            for (var i = 0; i < candidates.length; i += 1) {
                if (validReportSessionId(candidates[i])) return String(candidates[i]).trim()
            }
        } catch (e) {
        }
        return ""
    }

    function acceptReportActionRaw(raw) {
        root.sharedReportActionRaw = raw || ""
        var sid = root.reportSessionIdFromActionRaw(root.sharedReportActionRaw)
        if (root.validReportSessionId(sid)) {
            root.sharedSelectedReportSessionId = sid
        }
    }

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
    property string card1Widget1Type: String(layoutValue("card1_widget1_type", ""))
    property string card1Widget1Id: String(layoutValue("card1_widget1_id", ""))
    property string card1Widget1Label: String(layoutValue("card1_widget1_label", ""))
    property string card1Widget1Source: String(layoutValue("card1_widget1_source", ""))
    property string card1Widget1Fallback: String(layoutValue("card1_widget1_fallback", ""))
    property string card1Widget1Unit: String(layoutValue("card1_widget1_unit", ""))
    property string card1Widget1ActionId: String(layoutValue("card1_widget1_action_id", ""))
    property string card1Widget1ArgsJson: String(layoutValue("card1_widget1_args_json", "{}"))
    property string card1Widget1OptionsText: String(layoutValue("card1_widget1_options_text", ""))
    property string card1Widget1Variant: String(layoutValue("card1_widget1_variant", ""))
    property bool card1Widget1Required: Boolean(layoutValue("card1_widget1_required", false))
    property string card1Widget1Value: String(layoutValue("card1_widget1_value", ""))
    property string card1Widget2Type: String(layoutValue("card1_widget2_type", ""))
    property string card1Widget2Id: String(layoutValue("card1_widget2_id", ""))
    property string card1Widget2Label: String(layoutValue("card1_widget2_label", ""))
    property string card1Widget2Source: String(layoutValue("card1_widget2_source", ""))
    property string card1Widget2Fallback: String(layoutValue("card1_widget2_fallback", ""))
    property string card1Widget2Unit: String(layoutValue("card1_widget2_unit", ""))
    property string card1Widget2ActionId: String(layoutValue("card1_widget2_action_id", ""))
    property string card1Widget2ArgsJson: String(layoutValue("card1_widget2_args_json", "{}"))
    property string card1Widget2OptionsText: String(layoutValue("card1_widget2_options_text", ""))
    property string card1Widget2Variant: String(layoutValue("card1_widget2_variant", ""))
    property bool card1Widget2Required: Boolean(layoutValue("card1_widget2_required", false))
    property string card1Widget2Value: String(layoutValue("card1_widget2_value", ""))
    property string card1Widget3Type: String(layoutValue("card1_widget3_type", ""))
    property string card1Widget3Id: String(layoutValue("card1_widget3_id", ""))
    property string card1Widget3Label: String(layoutValue("card1_widget3_label", ""))
    property string card1Widget3Source: String(layoutValue("card1_widget3_source", ""))
    property string card1Widget3Fallback: String(layoutValue("card1_widget3_fallback", ""))
    property string card1Widget3Unit: String(layoutValue("card1_widget3_unit", ""))
    property string card1Widget3ActionId: String(layoutValue("card1_widget3_action_id", ""))
    property string card1Widget3ArgsJson: String(layoutValue("card1_widget3_args_json", "{}"))
    property string card1Widget3OptionsText: String(layoutValue("card1_widget3_options_text", ""))
    property string card1Widget3Variant: String(layoutValue("card1_widget3_variant", ""))
    property bool card1Widget3Required: Boolean(layoutValue("card1_widget3_required", false))
    property string card1Widget3Value: String(layoutValue("card1_widget3_value", ""))
    property string card1Widget4Type: String(layoutValue("card1_widget4_type", ""))
    property string card1Widget4Id: String(layoutValue("card1_widget4_id", ""))
    property string card1Widget4Label: String(layoutValue("card1_widget4_label", ""))
    property string card1Widget4Source: String(layoutValue("card1_widget4_source", ""))
    property string card1Widget4Fallback: String(layoutValue("card1_widget4_fallback", ""))
    property string card1Widget4Unit: String(layoutValue("card1_widget4_unit", ""))
    property string card1Widget4ActionId: String(layoutValue("card1_widget4_action_id", ""))
    property string card1Widget4ArgsJson: String(layoutValue("card1_widget4_args_json", "{}"))
    property string card1Widget4OptionsText: String(layoutValue("card1_widget4_options_text", ""))
    property string card1Widget4Variant: String(layoutValue("card1_widget4_variant", ""))
    property bool card1Widget4Required: Boolean(layoutValue("card1_widget4_required", false))
    property string card1Widget4Value: String(layoutValue("card1_widget4_value", ""))
    property string card1Widget5Type: String(layoutValue("card1_widget5_type", ""))
    property string card1Widget5Id: String(layoutValue("card1_widget5_id", ""))
    property string card1Widget5Label: String(layoutValue("card1_widget5_label", ""))
    property string card1Widget5Source: String(layoutValue("card1_widget5_source", ""))
    property string card1Widget5Fallback: String(layoutValue("card1_widget5_fallback", ""))
    property string card1Widget5Unit: String(layoutValue("card1_widget5_unit", ""))
    property string card1Widget5ActionId: String(layoutValue("card1_widget5_action_id", ""))
    property string card1Widget5ArgsJson: String(layoutValue("card1_widget5_args_json", "{}"))
    property string card1Widget5OptionsText: String(layoutValue("card1_widget5_options_text", ""))
    property string card1Widget5Variant: String(layoutValue("card1_widget5_variant", ""))
    property bool card1Widget5Required: Boolean(layoutValue("card1_widget5_required", false))
    property string card1Widget5Value: String(layoutValue("card1_widget5_value", ""))
    property string card1Widget6Type: String(layoutValue("card1_widget6_type", ""))
    property string card1Widget6Id: String(layoutValue("card1_widget6_id", ""))
    property string card1Widget6Label: String(layoutValue("card1_widget6_label", ""))
    property string card1Widget6Source: String(layoutValue("card1_widget6_source", ""))
    property string card1Widget6Fallback: String(layoutValue("card1_widget6_fallback", ""))
    property string card1Widget6Unit: String(layoutValue("card1_widget6_unit", ""))
    property string card1Widget6ActionId: String(layoutValue("card1_widget6_action_id", ""))
    property string card1Widget6ArgsJson: String(layoutValue("card1_widget6_args_json", "{}"))
    property string card1Widget6OptionsText: String(layoutValue("card1_widget6_options_text", ""))
    property string card1Widget6Variant: String(layoutValue("card1_widget6_variant", ""))
    property bool card1Widget6Required: Boolean(layoutValue("card1_widget6_required", false))
    property string card1Widget6Value: String(layoutValue("card1_widget6_value", ""))
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
    property string card2Widget1Type: String(layoutValue("card2_widget1_type", ""))
    property string card2Widget1Id: String(layoutValue("card2_widget1_id", ""))
    property string card2Widget1Label: String(layoutValue("card2_widget1_label", ""))
    property string card2Widget1Source: String(layoutValue("card2_widget1_source", ""))
    property string card2Widget1Fallback: String(layoutValue("card2_widget1_fallback", ""))
    property string card2Widget1Unit: String(layoutValue("card2_widget1_unit", ""))
    property string card2Widget1ActionId: String(layoutValue("card2_widget1_action_id", ""))
    property string card2Widget1ArgsJson: String(layoutValue("card2_widget1_args_json", "{}"))
    property string card2Widget1OptionsText: String(layoutValue("card2_widget1_options_text", ""))
    property string card2Widget1Variant: String(layoutValue("card2_widget1_variant", ""))
    property bool card2Widget1Required: Boolean(layoutValue("card2_widget1_required", false))
    property string card2Widget1Value: String(layoutValue("card2_widget1_value", ""))
    property string card2Widget2Type: String(layoutValue("card2_widget2_type", ""))
    property string card2Widget2Id: String(layoutValue("card2_widget2_id", ""))
    property string card2Widget2Label: String(layoutValue("card2_widget2_label", ""))
    property string card2Widget2Source: String(layoutValue("card2_widget2_source", ""))
    property string card2Widget2Fallback: String(layoutValue("card2_widget2_fallback", ""))
    property string card2Widget2Unit: String(layoutValue("card2_widget2_unit", ""))
    property string card2Widget2ActionId: String(layoutValue("card2_widget2_action_id", ""))
    property string card2Widget2ArgsJson: String(layoutValue("card2_widget2_args_json", "{}"))
    property string card2Widget2OptionsText: String(layoutValue("card2_widget2_options_text", ""))
    property string card2Widget2Variant: String(layoutValue("card2_widget2_variant", ""))
    property bool card2Widget2Required: Boolean(layoutValue("card2_widget2_required", false))
    property string card2Widget2Value: String(layoutValue("card2_widget2_value", ""))
    property string card2Widget3Type: String(layoutValue("card2_widget3_type", ""))
    property string card2Widget3Id: String(layoutValue("card2_widget3_id", ""))
    property string card2Widget3Label: String(layoutValue("card2_widget3_label", ""))
    property string card2Widget3Source: String(layoutValue("card2_widget3_source", ""))
    property string card2Widget3Fallback: String(layoutValue("card2_widget3_fallback", ""))
    property string card2Widget3Unit: String(layoutValue("card2_widget3_unit", ""))
    property string card2Widget3ActionId: String(layoutValue("card2_widget3_action_id", ""))
    property string card2Widget3ArgsJson: String(layoutValue("card2_widget3_args_json", "{}"))
    property string card2Widget3OptionsText: String(layoutValue("card2_widget3_options_text", ""))
    property string card2Widget3Variant: String(layoutValue("card2_widget3_variant", ""))
    property bool card2Widget3Required: Boolean(layoutValue("card2_widget3_required", false))
    property string card2Widget3Value: String(layoutValue("card2_widget3_value", ""))
    property string card2Widget4Type: String(layoutValue("card2_widget4_type", ""))
    property string card2Widget4Id: String(layoutValue("card2_widget4_id", ""))
    property string card2Widget4Label: String(layoutValue("card2_widget4_label", ""))
    property string card2Widget4Source: String(layoutValue("card2_widget4_source", ""))
    property string card2Widget4Fallback: String(layoutValue("card2_widget4_fallback", ""))
    property string card2Widget4Unit: String(layoutValue("card2_widget4_unit", ""))
    property string card2Widget4ActionId: String(layoutValue("card2_widget4_action_id", ""))
    property string card2Widget4ArgsJson: String(layoutValue("card2_widget4_args_json", "{}"))
    property string card2Widget4OptionsText: String(layoutValue("card2_widget4_options_text", ""))
    property string card2Widget4Variant: String(layoutValue("card2_widget4_variant", ""))
    property bool card2Widget4Required: Boolean(layoutValue("card2_widget4_required", false))
    property string card2Widget4Value: String(layoutValue("card2_widget4_value", ""))
    property string card2Widget5Type: String(layoutValue("card2_widget5_type", ""))
    property string card2Widget5Id: String(layoutValue("card2_widget5_id", ""))
    property string card2Widget5Label: String(layoutValue("card2_widget5_label", ""))
    property string card2Widget5Source: String(layoutValue("card2_widget5_source", ""))
    property string card2Widget5Fallback: String(layoutValue("card2_widget5_fallback", ""))
    property string card2Widget5Unit: String(layoutValue("card2_widget5_unit", ""))
    property string card2Widget5ActionId: String(layoutValue("card2_widget5_action_id", ""))
    property string card2Widget5ArgsJson: String(layoutValue("card2_widget5_args_json", "{}"))
    property string card2Widget5OptionsText: String(layoutValue("card2_widget5_options_text", ""))
    property string card2Widget5Variant: String(layoutValue("card2_widget5_variant", ""))
    property bool card2Widget5Required: Boolean(layoutValue("card2_widget5_required", false))
    property string card2Widget5Value: String(layoutValue("card2_widget5_value", ""))
    property string card2Widget6Type: String(layoutValue("card2_widget6_type", ""))
    property string card2Widget6Id: String(layoutValue("card2_widget6_id", ""))
    property string card2Widget6Label: String(layoutValue("card2_widget6_label", ""))
    property string card2Widget6Source: String(layoutValue("card2_widget6_source", ""))
    property string card2Widget6Fallback: String(layoutValue("card2_widget6_fallback", ""))
    property string card2Widget6Unit: String(layoutValue("card2_widget6_unit", ""))
    property string card2Widget6ActionId: String(layoutValue("card2_widget6_action_id", ""))
    property string card2Widget6ArgsJson: String(layoutValue("card2_widget6_args_json", "{}"))
    property string card2Widget6OptionsText: String(layoutValue("card2_widget6_options_text", ""))
    property string card2Widget6Variant: String(layoutValue("card2_widget6_variant", ""))
    property bool card2Widget6Required: Boolean(layoutValue("card2_widget6_required", false))
    property string card2Widget6Value: String(layoutValue("card2_widget6_value", ""))
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
    property string card3Widget1Type: String(layoutValue("card3_widget1_type", ""))
    property string card3Widget1Id: String(layoutValue("card3_widget1_id", ""))
    property string card3Widget1Label: String(layoutValue("card3_widget1_label", ""))
    property string card3Widget1Source: String(layoutValue("card3_widget1_source", ""))
    property string card3Widget1Fallback: String(layoutValue("card3_widget1_fallback", ""))
    property string card3Widget1Unit: String(layoutValue("card3_widget1_unit", ""))
    property string card3Widget1ActionId: String(layoutValue("card3_widget1_action_id", ""))
    property string card3Widget1ArgsJson: String(layoutValue("card3_widget1_args_json", "{}"))
    property string card3Widget1OptionsText: String(layoutValue("card3_widget1_options_text", ""))
    property string card3Widget1Variant: String(layoutValue("card3_widget1_variant", ""))
    property bool card3Widget1Required: Boolean(layoutValue("card3_widget1_required", false))
    property string card3Widget1Value: String(layoutValue("card3_widget1_value", ""))
    property string card3Widget2Type: String(layoutValue("card3_widget2_type", ""))
    property string card3Widget2Id: String(layoutValue("card3_widget2_id", ""))
    property string card3Widget2Label: String(layoutValue("card3_widget2_label", ""))
    property string card3Widget2Source: String(layoutValue("card3_widget2_source", ""))
    property string card3Widget2Fallback: String(layoutValue("card3_widget2_fallback", ""))
    property string card3Widget2Unit: String(layoutValue("card3_widget2_unit", ""))
    property string card3Widget2ActionId: String(layoutValue("card3_widget2_action_id", ""))
    property string card3Widget2ArgsJson: String(layoutValue("card3_widget2_args_json", "{}"))
    property string card3Widget2OptionsText: String(layoutValue("card3_widget2_options_text", ""))
    property string card3Widget2Variant: String(layoutValue("card3_widget2_variant", ""))
    property bool card3Widget2Required: Boolean(layoutValue("card3_widget2_required", false))
    property string card3Widget2Value: String(layoutValue("card3_widget2_value", ""))
    property string card3Widget3Type: String(layoutValue("card3_widget3_type", ""))
    property string card3Widget3Id: String(layoutValue("card3_widget3_id", ""))
    property string card3Widget3Label: String(layoutValue("card3_widget3_label", ""))
    property string card3Widget3Source: String(layoutValue("card3_widget3_source", ""))
    property string card3Widget3Fallback: String(layoutValue("card3_widget3_fallback", ""))
    property string card3Widget3Unit: String(layoutValue("card3_widget3_unit", ""))
    property string card3Widget3ActionId: String(layoutValue("card3_widget3_action_id", ""))
    property string card3Widget3ArgsJson: String(layoutValue("card3_widget3_args_json", "{}"))
    property string card3Widget3OptionsText: String(layoutValue("card3_widget3_options_text", ""))
    property string card3Widget3Variant: String(layoutValue("card3_widget3_variant", ""))
    property bool card3Widget3Required: Boolean(layoutValue("card3_widget3_required", false))
    property string card3Widget3Value: String(layoutValue("card3_widget3_value", ""))
    property string card3Widget4Type: String(layoutValue("card3_widget4_type", ""))
    property string card3Widget4Id: String(layoutValue("card3_widget4_id", ""))
    property string card3Widget4Label: String(layoutValue("card3_widget4_label", ""))
    property string card3Widget4Source: String(layoutValue("card3_widget4_source", ""))
    property string card3Widget4Fallback: String(layoutValue("card3_widget4_fallback", ""))
    property string card3Widget4Unit: String(layoutValue("card3_widget4_unit", ""))
    property string card3Widget4ActionId: String(layoutValue("card3_widget4_action_id", ""))
    property string card3Widget4ArgsJson: String(layoutValue("card3_widget4_args_json", "{}"))
    property string card3Widget4OptionsText: String(layoutValue("card3_widget4_options_text", ""))
    property string card3Widget4Variant: String(layoutValue("card3_widget4_variant", ""))
    property bool card3Widget4Required: Boolean(layoutValue("card3_widget4_required", false))
    property string card3Widget4Value: String(layoutValue("card3_widget4_value", ""))
    property string card3Widget5Type: String(layoutValue("card3_widget5_type", ""))
    property string card3Widget5Id: String(layoutValue("card3_widget5_id", ""))
    property string card3Widget5Label: String(layoutValue("card3_widget5_label", ""))
    property string card3Widget5Source: String(layoutValue("card3_widget5_source", ""))
    property string card3Widget5Fallback: String(layoutValue("card3_widget5_fallback", ""))
    property string card3Widget5Unit: String(layoutValue("card3_widget5_unit", ""))
    property string card3Widget5ActionId: String(layoutValue("card3_widget5_action_id", ""))
    property string card3Widget5ArgsJson: String(layoutValue("card3_widget5_args_json", "{}"))
    property string card3Widget5OptionsText: String(layoutValue("card3_widget5_options_text", ""))
    property string card3Widget5Variant: String(layoutValue("card3_widget5_variant", ""))
    property bool card3Widget5Required: Boolean(layoutValue("card3_widget5_required", false))
    property string card3Widget5Value: String(layoutValue("card3_widget5_value", ""))
    property string card3Widget6Type: String(layoutValue("card3_widget6_type", ""))
    property string card3Widget6Id: String(layoutValue("card3_widget6_id", ""))
    property string card3Widget6Label: String(layoutValue("card3_widget6_label", ""))
    property string card3Widget6Source: String(layoutValue("card3_widget6_source", ""))
    property string card3Widget6Fallback: String(layoutValue("card3_widget6_fallback", ""))
    property string card3Widget6Unit: String(layoutValue("card3_widget6_unit", ""))
    property string card3Widget6ActionId: String(layoutValue("card3_widget6_action_id", ""))
    property string card3Widget6ArgsJson: String(layoutValue("card3_widget6_args_json", "{}"))
    property string card3Widget6OptionsText: String(layoutValue("card3_widget6_options_text", ""))
    property string card3Widget6Variant: String(layoutValue("card3_widget6_variant", ""))
    property bool card3Widget6Required: Boolean(layoutValue("card3_widget6_required", false))
    property string card3Widget6Value: String(layoutValue("card3_widget6_value", ""))
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
    property string card4Widget1Type: String(layoutValue("card4_widget1_type", ""))
    property string card4Widget1Id: String(layoutValue("card4_widget1_id", ""))
    property string card4Widget1Label: String(layoutValue("card4_widget1_label", ""))
    property string card4Widget1Source: String(layoutValue("card4_widget1_source", ""))
    property string card4Widget1Fallback: String(layoutValue("card4_widget1_fallback", ""))
    property string card4Widget1Unit: String(layoutValue("card4_widget1_unit", ""))
    property string card4Widget1ActionId: String(layoutValue("card4_widget1_action_id", ""))
    property string card4Widget1ArgsJson: String(layoutValue("card4_widget1_args_json", "{}"))
    property string card4Widget1OptionsText: String(layoutValue("card4_widget1_options_text", ""))
    property string card4Widget1Variant: String(layoutValue("card4_widget1_variant", ""))
    property bool card4Widget1Required: Boolean(layoutValue("card4_widget1_required", false))
    property string card4Widget1Value: String(layoutValue("card4_widget1_value", ""))
    property string card4Widget2Type: String(layoutValue("card4_widget2_type", ""))
    property string card4Widget2Id: String(layoutValue("card4_widget2_id", ""))
    property string card4Widget2Label: String(layoutValue("card4_widget2_label", ""))
    property string card4Widget2Source: String(layoutValue("card4_widget2_source", ""))
    property string card4Widget2Fallback: String(layoutValue("card4_widget2_fallback", ""))
    property string card4Widget2Unit: String(layoutValue("card4_widget2_unit", ""))
    property string card4Widget2ActionId: String(layoutValue("card4_widget2_action_id", ""))
    property string card4Widget2ArgsJson: String(layoutValue("card4_widget2_args_json", "{}"))
    property string card4Widget2OptionsText: String(layoutValue("card4_widget2_options_text", ""))
    property string card4Widget2Variant: String(layoutValue("card4_widget2_variant", ""))
    property bool card4Widget2Required: Boolean(layoutValue("card4_widget2_required", false))
    property string card4Widget2Value: String(layoutValue("card4_widget2_value", ""))
    property string card4Widget3Type: String(layoutValue("card4_widget3_type", ""))
    property string card4Widget3Id: String(layoutValue("card4_widget3_id", ""))
    property string card4Widget3Label: String(layoutValue("card4_widget3_label", ""))
    property string card4Widget3Source: String(layoutValue("card4_widget3_source", ""))
    property string card4Widget3Fallback: String(layoutValue("card4_widget3_fallback", ""))
    property string card4Widget3Unit: String(layoutValue("card4_widget3_unit", ""))
    property string card4Widget3ActionId: String(layoutValue("card4_widget3_action_id", ""))
    property string card4Widget3ArgsJson: String(layoutValue("card4_widget3_args_json", "{}"))
    property string card4Widget3OptionsText: String(layoutValue("card4_widget3_options_text", ""))
    property string card4Widget3Variant: String(layoutValue("card4_widget3_variant", ""))
    property bool card4Widget3Required: Boolean(layoutValue("card4_widget3_required", false))
    property string card4Widget3Value: String(layoutValue("card4_widget3_value", ""))
    property string card4Widget4Type: String(layoutValue("card4_widget4_type", ""))
    property string card4Widget4Id: String(layoutValue("card4_widget4_id", ""))
    property string card4Widget4Label: String(layoutValue("card4_widget4_label", ""))
    property string card4Widget4Source: String(layoutValue("card4_widget4_source", ""))
    property string card4Widget4Fallback: String(layoutValue("card4_widget4_fallback", ""))
    property string card4Widget4Unit: String(layoutValue("card4_widget4_unit", ""))
    property string card4Widget4ActionId: String(layoutValue("card4_widget4_action_id", ""))
    property string card4Widget4ArgsJson: String(layoutValue("card4_widget4_args_json", "{}"))
    property string card4Widget4OptionsText: String(layoutValue("card4_widget4_options_text", ""))
    property string card4Widget4Variant: String(layoutValue("card4_widget4_variant", ""))
    property bool card4Widget4Required: Boolean(layoutValue("card4_widget4_required", false))
    property string card4Widget4Value: String(layoutValue("card4_widget4_value", ""))
    property string card4Widget5Type: String(layoutValue("card4_widget5_type", ""))
    property string card4Widget5Id: String(layoutValue("card4_widget5_id", ""))
    property string card4Widget5Label: String(layoutValue("card4_widget5_label", ""))
    property string card4Widget5Source: String(layoutValue("card4_widget5_source", ""))
    property string card4Widget5Fallback: String(layoutValue("card4_widget5_fallback", ""))
    property string card4Widget5Unit: String(layoutValue("card4_widget5_unit", ""))
    property string card4Widget5ActionId: String(layoutValue("card4_widget5_action_id", ""))
    property string card4Widget5ArgsJson: String(layoutValue("card4_widget5_args_json", "{}"))
    property string card4Widget5OptionsText: String(layoutValue("card4_widget5_options_text", ""))
    property string card4Widget5Variant: String(layoutValue("card4_widget5_variant", ""))
    property bool card4Widget5Required: Boolean(layoutValue("card4_widget5_required", false))
    property string card4Widget5Value: String(layoutValue("card4_widget5_value", ""))
    property string card4Widget6Type: String(layoutValue("card4_widget6_type", ""))
    property string card4Widget6Id: String(layoutValue("card4_widget6_id", ""))
    property string card4Widget6Label: String(layoutValue("card4_widget6_label", ""))
    property string card4Widget6Source: String(layoutValue("card4_widget6_source", ""))
    property string card4Widget6Fallback: String(layoutValue("card4_widget6_fallback", ""))
    property string card4Widget6Unit: String(layoutValue("card4_widget6_unit", ""))
    property string card4Widget6ActionId: String(layoutValue("card4_widget6_action_id", ""))
    property string card4Widget6ArgsJson: String(layoutValue("card4_widget6_args_json", "{}"))
    property string card4Widget6OptionsText: String(layoutValue("card4_widget6_options_text", ""))
    property string card4Widget6Variant: String(layoutValue("card4_widget6_variant", ""))
    property bool card4Widget6Required: Boolean(layoutValue("card4_widget6_required", false))
    property string card4Widget6Value: String(layoutValue("card4_widget6_value", ""))
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
    property string card5Widget1Type: String(layoutValue("card5_widget1_type", ""))
    property string card5Widget1Id: String(layoutValue("card5_widget1_id", ""))
    property string card5Widget1Label: String(layoutValue("card5_widget1_label", ""))
    property string card5Widget1Source: String(layoutValue("card5_widget1_source", ""))
    property string card5Widget1Fallback: String(layoutValue("card5_widget1_fallback", ""))
    property string card5Widget1Unit: String(layoutValue("card5_widget1_unit", ""))
    property string card5Widget1ActionId: String(layoutValue("card5_widget1_action_id", ""))
    property string card5Widget1ArgsJson: String(layoutValue("card5_widget1_args_json", "{}"))
    property string card5Widget1OptionsText: String(layoutValue("card5_widget1_options_text", ""))
    property string card5Widget1Variant: String(layoutValue("card5_widget1_variant", ""))
    property bool card5Widget1Required: Boolean(layoutValue("card5_widget1_required", false))
    property string card5Widget1Value: String(layoutValue("card5_widget1_value", ""))
    property string card5Widget2Type: String(layoutValue("card5_widget2_type", ""))
    property string card5Widget2Id: String(layoutValue("card5_widget2_id", ""))
    property string card5Widget2Label: String(layoutValue("card5_widget2_label", ""))
    property string card5Widget2Source: String(layoutValue("card5_widget2_source", ""))
    property string card5Widget2Fallback: String(layoutValue("card5_widget2_fallback", ""))
    property string card5Widget2Unit: String(layoutValue("card5_widget2_unit", ""))
    property string card5Widget2ActionId: String(layoutValue("card5_widget2_action_id", ""))
    property string card5Widget2ArgsJson: String(layoutValue("card5_widget2_args_json", "{}"))
    property string card5Widget2OptionsText: String(layoutValue("card5_widget2_options_text", ""))
    property string card5Widget2Variant: String(layoutValue("card5_widget2_variant", ""))
    property bool card5Widget2Required: Boolean(layoutValue("card5_widget2_required", false))
    property string card5Widget2Value: String(layoutValue("card5_widget2_value", ""))
    property string card5Widget3Type: String(layoutValue("card5_widget3_type", ""))
    property string card5Widget3Id: String(layoutValue("card5_widget3_id", ""))
    property string card5Widget3Label: String(layoutValue("card5_widget3_label", ""))
    property string card5Widget3Source: String(layoutValue("card5_widget3_source", ""))
    property string card5Widget3Fallback: String(layoutValue("card5_widget3_fallback", ""))
    property string card5Widget3Unit: String(layoutValue("card5_widget3_unit", ""))
    property string card5Widget3ActionId: String(layoutValue("card5_widget3_action_id", ""))
    property string card5Widget3ArgsJson: String(layoutValue("card5_widget3_args_json", "{}"))
    property string card5Widget3OptionsText: String(layoutValue("card5_widget3_options_text", ""))
    property string card5Widget3Variant: String(layoutValue("card5_widget3_variant", ""))
    property bool card5Widget3Required: Boolean(layoutValue("card5_widget3_required", false))
    property string card5Widget3Value: String(layoutValue("card5_widget3_value", ""))
    property string card5Widget4Type: String(layoutValue("card5_widget4_type", ""))
    property string card5Widget4Id: String(layoutValue("card5_widget4_id", ""))
    property string card5Widget4Label: String(layoutValue("card5_widget4_label", ""))
    property string card5Widget4Source: String(layoutValue("card5_widget4_source", ""))
    property string card5Widget4Fallback: String(layoutValue("card5_widget4_fallback", ""))
    property string card5Widget4Unit: String(layoutValue("card5_widget4_unit", ""))
    property string card5Widget4ActionId: String(layoutValue("card5_widget4_action_id", ""))
    property string card5Widget4ArgsJson: String(layoutValue("card5_widget4_args_json", "{}"))
    property string card5Widget4OptionsText: String(layoutValue("card5_widget4_options_text", ""))
    property string card5Widget4Variant: String(layoutValue("card5_widget4_variant", ""))
    property bool card5Widget4Required: Boolean(layoutValue("card5_widget4_required", false))
    property string card5Widget4Value: String(layoutValue("card5_widget4_value", ""))
    property string card5Widget5Type: String(layoutValue("card5_widget5_type", ""))
    property string card5Widget5Id: String(layoutValue("card5_widget5_id", ""))
    property string card5Widget5Label: String(layoutValue("card5_widget5_label", ""))
    property string card5Widget5Source: String(layoutValue("card5_widget5_source", ""))
    property string card5Widget5Fallback: String(layoutValue("card5_widget5_fallback", ""))
    property string card5Widget5Unit: String(layoutValue("card5_widget5_unit", ""))
    property string card5Widget5ActionId: String(layoutValue("card5_widget5_action_id", ""))
    property string card5Widget5ArgsJson: String(layoutValue("card5_widget5_args_json", "{}"))
    property string card5Widget5OptionsText: String(layoutValue("card5_widget5_options_text", ""))
    property string card5Widget5Variant: String(layoutValue("card5_widget5_variant", ""))
    property bool card5Widget5Required: Boolean(layoutValue("card5_widget5_required", false))
    property string card5Widget5Value: String(layoutValue("card5_widget5_value", ""))
    property string card5Widget6Type: String(layoutValue("card5_widget6_type", ""))
    property string card5Widget6Id: String(layoutValue("card5_widget6_id", ""))
    property string card5Widget6Label: String(layoutValue("card5_widget6_label", ""))
    property string card5Widget6Source: String(layoutValue("card5_widget6_source", ""))
    property string card5Widget6Fallback: String(layoutValue("card5_widget6_fallback", ""))
    property string card5Widget6Unit: String(layoutValue("card5_widget6_unit", ""))
    property string card5Widget6ActionId: String(layoutValue("card5_widget6_action_id", ""))
    property string card5Widget6ArgsJson: String(layoutValue("card5_widget6_args_json", "{}"))
    property string card5Widget6OptionsText: String(layoutValue("card5_widget6_options_text", ""))
    property string card5Widget6Variant: String(layoutValue("card5_widget6_variant", ""))
    property bool card5Widget6Required: Boolean(layoutValue("card5_widget6_required", false))
    property string card5Widget6Value: String(layoutValue("card5_widget6_value", ""))
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
    property string card6Widget1Type: String(layoutValue("card6_widget1_type", ""))
    property string card6Widget1Id: String(layoutValue("card6_widget1_id", ""))
    property string card6Widget1Label: String(layoutValue("card6_widget1_label", ""))
    property string card6Widget1Source: String(layoutValue("card6_widget1_source", ""))
    property string card6Widget1Fallback: String(layoutValue("card6_widget1_fallback", ""))
    property string card6Widget1Unit: String(layoutValue("card6_widget1_unit", ""))
    property string card6Widget1ActionId: String(layoutValue("card6_widget1_action_id", ""))
    property string card6Widget1ArgsJson: String(layoutValue("card6_widget1_args_json", "{}"))
    property string card6Widget1OptionsText: String(layoutValue("card6_widget1_options_text", ""))
    property string card6Widget1Variant: String(layoutValue("card6_widget1_variant", ""))
    property bool card6Widget1Required: Boolean(layoutValue("card6_widget1_required", false))
    property string card6Widget1Value: String(layoutValue("card6_widget1_value", ""))
    property string card6Widget2Type: String(layoutValue("card6_widget2_type", ""))
    property string card6Widget2Id: String(layoutValue("card6_widget2_id", ""))
    property string card6Widget2Label: String(layoutValue("card6_widget2_label", ""))
    property string card6Widget2Source: String(layoutValue("card6_widget2_source", ""))
    property string card6Widget2Fallback: String(layoutValue("card6_widget2_fallback", ""))
    property string card6Widget2Unit: String(layoutValue("card6_widget2_unit", ""))
    property string card6Widget2ActionId: String(layoutValue("card6_widget2_action_id", ""))
    property string card6Widget2ArgsJson: String(layoutValue("card6_widget2_args_json", "{}"))
    property string card6Widget2OptionsText: String(layoutValue("card6_widget2_options_text", ""))
    property string card6Widget2Variant: String(layoutValue("card6_widget2_variant", ""))
    property bool card6Widget2Required: Boolean(layoutValue("card6_widget2_required", false))
    property string card6Widget2Value: String(layoutValue("card6_widget2_value", ""))
    property string card6Widget3Type: String(layoutValue("card6_widget3_type", ""))
    property string card6Widget3Id: String(layoutValue("card6_widget3_id", ""))
    property string card6Widget3Label: String(layoutValue("card6_widget3_label", ""))
    property string card6Widget3Source: String(layoutValue("card6_widget3_source", ""))
    property string card6Widget3Fallback: String(layoutValue("card6_widget3_fallback", ""))
    property string card6Widget3Unit: String(layoutValue("card6_widget3_unit", ""))
    property string card6Widget3ActionId: String(layoutValue("card6_widget3_action_id", ""))
    property string card6Widget3ArgsJson: String(layoutValue("card6_widget3_args_json", "{}"))
    property string card6Widget3OptionsText: String(layoutValue("card6_widget3_options_text", ""))
    property string card6Widget3Variant: String(layoutValue("card6_widget3_variant", ""))
    property bool card6Widget3Required: Boolean(layoutValue("card6_widget3_required", false))
    property string card6Widget3Value: String(layoutValue("card6_widget3_value", ""))
    property string card6Widget4Type: String(layoutValue("card6_widget4_type", ""))
    property string card6Widget4Id: String(layoutValue("card6_widget4_id", ""))
    property string card6Widget4Label: String(layoutValue("card6_widget4_label", ""))
    property string card6Widget4Source: String(layoutValue("card6_widget4_source", ""))
    property string card6Widget4Fallback: String(layoutValue("card6_widget4_fallback", ""))
    property string card6Widget4Unit: String(layoutValue("card6_widget4_unit", ""))
    property string card6Widget4ActionId: String(layoutValue("card6_widget4_action_id", ""))
    property string card6Widget4ArgsJson: String(layoutValue("card6_widget4_args_json", "{}"))
    property string card6Widget4OptionsText: String(layoutValue("card6_widget4_options_text", ""))
    property string card6Widget4Variant: String(layoutValue("card6_widget4_variant", ""))
    property bool card6Widget4Required: Boolean(layoutValue("card6_widget4_required", false))
    property string card6Widget4Value: String(layoutValue("card6_widget4_value", ""))
    property string card6Widget5Type: String(layoutValue("card6_widget5_type", ""))
    property string card6Widget5Id: String(layoutValue("card6_widget5_id", ""))
    property string card6Widget5Label: String(layoutValue("card6_widget5_label", ""))
    property string card6Widget5Source: String(layoutValue("card6_widget5_source", ""))
    property string card6Widget5Fallback: String(layoutValue("card6_widget5_fallback", ""))
    property string card6Widget5Unit: String(layoutValue("card6_widget5_unit", ""))
    property string card6Widget5ActionId: String(layoutValue("card6_widget5_action_id", ""))
    property string card6Widget5ArgsJson: String(layoutValue("card6_widget5_args_json", "{}"))
    property string card6Widget5OptionsText: String(layoutValue("card6_widget5_options_text", ""))
    property string card6Widget5Variant: String(layoutValue("card6_widget5_variant", ""))
    property bool card6Widget5Required: Boolean(layoutValue("card6_widget5_required", false))
    property string card6Widget5Value: String(layoutValue("card6_widget5_value", ""))
    property string card6Widget6Type: String(layoutValue("card6_widget6_type", ""))
    property string card6Widget6Id: String(layoutValue("card6_widget6_id", ""))
    property string card6Widget6Label: String(layoutValue("card6_widget6_label", ""))
    property string card6Widget6Source: String(layoutValue("card6_widget6_source", ""))
    property string card6Widget6Fallback: String(layoutValue("card6_widget6_fallback", ""))
    property string card6Widget6Unit: String(layoutValue("card6_widget6_unit", ""))
    property string card6Widget6ActionId: String(layoutValue("card6_widget6_action_id", ""))
    property string card6Widget6ArgsJson: String(layoutValue("card6_widget6_args_json", "{}"))
    property string card6Widget6OptionsText: String(layoutValue("card6_widget6_options_text", ""))
    property string card6Widget6Variant: String(layoutValue("card6_widget6_variant", ""))
    property bool card6Widget6Required: Boolean(layoutValue("card6_widget6_required", false))
    property string card6Widget6Value: String(layoutValue("card6_widget6_value", ""))
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
    property string card7Widget1Type: String(layoutValue("card7_widget1_type", ""))
    property string card7Widget1Id: String(layoutValue("card7_widget1_id", ""))
    property string card7Widget1Label: String(layoutValue("card7_widget1_label", ""))
    property string card7Widget1Source: String(layoutValue("card7_widget1_source", ""))
    property string card7Widget1Fallback: String(layoutValue("card7_widget1_fallback", ""))
    property string card7Widget1Unit: String(layoutValue("card7_widget1_unit", ""))
    property string card7Widget1ActionId: String(layoutValue("card7_widget1_action_id", ""))
    property string card7Widget1ArgsJson: String(layoutValue("card7_widget1_args_json", "{}"))
    property string card7Widget1OptionsText: String(layoutValue("card7_widget1_options_text", ""))
    property string card7Widget1Variant: String(layoutValue("card7_widget1_variant", ""))
    property bool card7Widget1Required: Boolean(layoutValue("card7_widget1_required", false))
    property string card7Widget1Value: String(layoutValue("card7_widget1_value", ""))
    property string card7Widget2Type: String(layoutValue("card7_widget2_type", ""))
    property string card7Widget2Id: String(layoutValue("card7_widget2_id", ""))
    property string card7Widget2Label: String(layoutValue("card7_widget2_label", ""))
    property string card7Widget2Source: String(layoutValue("card7_widget2_source", ""))
    property string card7Widget2Fallback: String(layoutValue("card7_widget2_fallback", ""))
    property string card7Widget2Unit: String(layoutValue("card7_widget2_unit", ""))
    property string card7Widget2ActionId: String(layoutValue("card7_widget2_action_id", ""))
    property string card7Widget2ArgsJson: String(layoutValue("card7_widget2_args_json", "{}"))
    property string card7Widget2OptionsText: String(layoutValue("card7_widget2_options_text", ""))
    property string card7Widget2Variant: String(layoutValue("card7_widget2_variant", ""))
    property bool card7Widget2Required: Boolean(layoutValue("card7_widget2_required", false))
    property string card7Widget2Value: String(layoutValue("card7_widget2_value", ""))
    property string card7Widget3Type: String(layoutValue("card7_widget3_type", ""))
    property string card7Widget3Id: String(layoutValue("card7_widget3_id", ""))
    property string card7Widget3Label: String(layoutValue("card7_widget3_label", ""))
    property string card7Widget3Source: String(layoutValue("card7_widget3_source", ""))
    property string card7Widget3Fallback: String(layoutValue("card7_widget3_fallback", ""))
    property string card7Widget3Unit: String(layoutValue("card7_widget3_unit", ""))
    property string card7Widget3ActionId: String(layoutValue("card7_widget3_action_id", ""))
    property string card7Widget3ArgsJson: String(layoutValue("card7_widget3_args_json", "{}"))
    property string card7Widget3OptionsText: String(layoutValue("card7_widget3_options_text", ""))
    property string card7Widget3Variant: String(layoutValue("card7_widget3_variant", ""))
    property bool card7Widget3Required: Boolean(layoutValue("card7_widget3_required", false))
    property string card7Widget3Value: String(layoutValue("card7_widget3_value", ""))
    property string card7Widget4Type: String(layoutValue("card7_widget4_type", ""))
    property string card7Widget4Id: String(layoutValue("card7_widget4_id", ""))
    property string card7Widget4Label: String(layoutValue("card7_widget4_label", ""))
    property string card7Widget4Source: String(layoutValue("card7_widget4_source", ""))
    property string card7Widget4Fallback: String(layoutValue("card7_widget4_fallback", ""))
    property string card7Widget4Unit: String(layoutValue("card7_widget4_unit", ""))
    property string card7Widget4ActionId: String(layoutValue("card7_widget4_action_id", ""))
    property string card7Widget4ArgsJson: String(layoutValue("card7_widget4_args_json", "{}"))
    property string card7Widget4OptionsText: String(layoutValue("card7_widget4_options_text", ""))
    property string card7Widget4Variant: String(layoutValue("card7_widget4_variant", ""))
    property bool card7Widget4Required: Boolean(layoutValue("card7_widget4_required", false))
    property string card7Widget4Value: String(layoutValue("card7_widget4_value", ""))
    property string card7Widget5Type: String(layoutValue("card7_widget5_type", ""))
    property string card7Widget5Id: String(layoutValue("card7_widget5_id", ""))
    property string card7Widget5Label: String(layoutValue("card7_widget5_label", ""))
    property string card7Widget5Source: String(layoutValue("card7_widget5_source", ""))
    property string card7Widget5Fallback: String(layoutValue("card7_widget5_fallback", ""))
    property string card7Widget5Unit: String(layoutValue("card7_widget5_unit", ""))
    property string card7Widget5ActionId: String(layoutValue("card7_widget5_action_id", ""))
    property string card7Widget5ArgsJson: String(layoutValue("card7_widget5_args_json", "{}"))
    property string card7Widget5OptionsText: String(layoutValue("card7_widget5_options_text", ""))
    property string card7Widget5Variant: String(layoutValue("card7_widget5_variant", ""))
    property bool card7Widget5Required: Boolean(layoutValue("card7_widget5_required", false))
    property string card7Widget5Value: String(layoutValue("card7_widget5_value", ""))
    property string card7Widget6Type: String(layoutValue("card7_widget6_type", ""))
    property string card7Widget6Id: String(layoutValue("card7_widget6_id", ""))
    property string card7Widget6Label: String(layoutValue("card7_widget6_label", ""))
    property string card7Widget6Source: String(layoutValue("card7_widget6_source", ""))
    property string card7Widget6Fallback: String(layoutValue("card7_widget6_fallback", ""))
    property string card7Widget6Unit: String(layoutValue("card7_widget6_unit", ""))
    property string card7Widget6ActionId: String(layoutValue("card7_widget6_action_id", ""))
    property string card7Widget6ArgsJson: String(layoutValue("card7_widget6_args_json", "{}"))
    property string card7Widget6OptionsText: String(layoutValue("card7_widget6_options_text", ""))
    property string card7Widget6Variant: String(layoutValue("card7_widget6_variant", ""))
    property bool card7Widget6Required: Boolean(layoutValue("card7_widget6_required", false))
    property string card7Widget6Value: String(layoutValue("card7_widget6_value", ""))

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
    property int card1TitlePixelSize: Number(layoutValue("card1_title_pixel_size", 15))
    property int card1SubtitlePixelSize: Number(layoutValue("card1_subtitle_pixel_size", 10))
    property int card1WidgetLabelPixelSize: Number(layoutValue("card1_widget_label_pixel_size", 10))
    property int card1WidgetValuePixelSize: Number(layoutValue("card1_widget_value_pixel_size", 12))
    property int card1WidgetMetaPixelSize: Number(layoutValue("card1_widget_meta_pixel_size", 9))
    property int card1WidgetRowHeight: Number(layoutValue("card1_widget_row_height", 22))
    property int card1ButtonHeight: Number(layoutValue("card1_button_height", 28))
    property int card1WidgetSpacing: Number(layoutValue("card1_widget_spacing", 3))
    property int card1BodyTopMargin: Number(layoutValue("card1_body_top_margin", 2))
    property int card1FeedbackHeight: Number(layoutValue("card1_feedback_height", 34))
    property int card1FeedbackPixelSize: Number(layoutValue("card1_feedback_pixel_size", 9))
    property int card1HeaderSpacing: Number(layoutValue("card1_header_spacing", 2))
    property int card1ContentSpacing: Number(layoutValue("card1_content_spacing", 4))
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
    property int card2TitlePixelSize: Number(layoutValue("card2_title_pixel_size", 15))
    property int card2SubtitlePixelSize: Number(layoutValue("card2_subtitle_pixel_size", 10))
    property int card2WidgetLabelPixelSize: Number(layoutValue("card2_widget_label_pixel_size", 10))
    property int card2WidgetValuePixelSize: Number(layoutValue("card2_widget_value_pixel_size", 12))
    property int card2WidgetMetaPixelSize: Number(layoutValue("card2_widget_meta_pixel_size", 9))
    property int card2WidgetRowHeight: Number(layoutValue("card2_widget_row_height", 22))
    property int card2ButtonHeight: Number(layoutValue("card2_button_height", 28))
    property int card2WidgetSpacing: Number(layoutValue("card2_widget_spacing", 3))
    property int card2BodyTopMargin: Number(layoutValue("card2_body_top_margin", 2))
    property int card2FeedbackHeight: Number(layoutValue("card2_feedback_height", 34))
    property int card2FeedbackPixelSize: Number(layoutValue("card2_feedback_pixel_size", 9))
    property int card2HeaderSpacing: Number(layoutValue("card2_header_spacing", 2))
    property int card2ContentSpacing: Number(layoutValue("card2_content_spacing", 4))
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
    property int card3TitlePixelSize: Number(layoutValue("card3_title_pixel_size", 15))
    property int card3SubtitlePixelSize: Number(layoutValue("card3_subtitle_pixel_size", 10))
    property int card3WidgetLabelPixelSize: Number(layoutValue("card3_widget_label_pixel_size", 10))
    property int card3WidgetValuePixelSize: Number(layoutValue("card3_widget_value_pixel_size", 12))
    property int card3WidgetMetaPixelSize: Number(layoutValue("card3_widget_meta_pixel_size", 9))
    property int card3WidgetRowHeight: Number(layoutValue("card3_widget_row_height", 22))
    property int card3ButtonHeight: Number(layoutValue("card3_button_height", 28))
    property int card3WidgetSpacing: Number(layoutValue("card3_widget_spacing", 3))
    property int card3BodyTopMargin: Number(layoutValue("card3_body_top_margin", 2))
    property int card3FeedbackHeight: Number(layoutValue("card3_feedback_height", 34))
    property int card3FeedbackPixelSize: Number(layoutValue("card3_feedback_pixel_size", 9))
    property int card3HeaderSpacing: Number(layoutValue("card3_header_spacing", 2))
    property int card3ContentSpacing: Number(layoutValue("card3_content_spacing", 4))
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
    property int card4TitlePixelSize: Number(layoutValue("card4_title_pixel_size", 15))
    property int card4SubtitlePixelSize: Number(layoutValue("card4_subtitle_pixel_size", 10))
    property int card4WidgetLabelPixelSize: Number(layoutValue("card4_widget_label_pixel_size", 10))
    property int card4WidgetValuePixelSize: Number(layoutValue("card4_widget_value_pixel_size", 12))
    property int card4WidgetMetaPixelSize: Number(layoutValue("card4_widget_meta_pixel_size", 9))
    property int card4WidgetRowHeight: Number(layoutValue("card4_widget_row_height", 22))
    property int card4ButtonHeight: Number(layoutValue("card4_button_height", 28))
    property int card4WidgetSpacing: Number(layoutValue("card4_widget_spacing", 3))
    property int card4BodyTopMargin: Number(layoutValue("card4_body_top_margin", 2))
    property int card4FeedbackHeight: Number(layoutValue("card4_feedback_height", 34))
    property int card4FeedbackPixelSize: Number(layoutValue("card4_feedback_pixel_size", 9))
    property int card4HeaderSpacing: Number(layoutValue("card4_header_spacing", 2))
    property int card4ContentSpacing: Number(layoutValue("card4_content_spacing", 4))
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
    property int card5TitlePixelSize: Number(layoutValue("card5_title_pixel_size", 15))
    property int card5SubtitlePixelSize: Number(layoutValue("card5_subtitle_pixel_size", 10))
    property int card5WidgetLabelPixelSize: Number(layoutValue("card5_widget_label_pixel_size", 10))
    property int card5WidgetValuePixelSize: Number(layoutValue("card5_widget_value_pixel_size", 12))
    property int card5WidgetMetaPixelSize: Number(layoutValue("card5_widget_meta_pixel_size", 9))
    property int card5WidgetRowHeight: Number(layoutValue("card5_widget_row_height", 22))
    property int card5ButtonHeight: Number(layoutValue("card5_button_height", 28))
    property int card5WidgetSpacing: Number(layoutValue("card5_widget_spacing", 3))
    property int card5BodyTopMargin: Number(layoutValue("card5_body_top_margin", 2))
    property int card5FeedbackHeight: Number(layoutValue("card5_feedback_height", 34))
    property int card5FeedbackPixelSize: Number(layoutValue("card5_feedback_pixel_size", 9))
    property int card5HeaderSpacing: Number(layoutValue("card5_header_spacing", 2))
    property int card5ContentSpacing: Number(layoutValue("card5_content_spacing", 4))
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
    property int card6TitlePixelSize: Number(layoutValue("card6_title_pixel_size", 15))
    property int card6SubtitlePixelSize: Number(layoutValue("card6_subtitle_pixel_size", 10))
    property int card6WidgetLabelPixelSize: Number(layoutValue("card6_widget_label_pixel_size", 10))
    property int card6WidgetValuePixelSize: Number(layoutValue("card6_widget_value_pixel_size", 12))
    property int card6WidgetMetaPixelSize: Number(layoutValue("card6_widget_meta_pixel_size", 9))
    property int card6WidgetRowHeight: Number(layoutValue("card6_widget_row_height", 22))
    property int card6ButtonHeight: Number(layoutValue("card6_button_height", 28))
    property int card6WidgetSpacing: Number(layoutValue("card6_widget_spacing", 3))
    property int card6BodyTopMargin: Number(layoutValue("card6_body_top_margin", 2))
    property int card6FeedbackHeight: Number(layoutValue("card6_feedback_height", 34))
    property int card6FeedbackPixelSize: Number(layoutValue("card6_feedback_pixel_size", 9))
    property int card6HeaderSpacing: Number(layoutValue("card6_header_spacing", 2))
    property int card6ContentSpacing: Number(layoutValue("card6_content_spacing", 4))
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
    property int card7TitlePixelSize: Number(layoutValue("card7_title_pixel_size", 15))
    property int card7SubtitlePixelSize: Number(layoutValue("card7_subtitle_pixel_size", 10))
    property int card7WidgetLabelPixelSize: Number(layoutValue("card7_widget_label_pixel_size", 10))
    property int card7WidgetValuePixelSize: Number(layoutValue("card7_widget_value_pixel_size", 12))
    property int card7WidgetMetaPixelSize: Number(layoutValue("card7_widget_meta_pixel_size", 9))
    property int card7WidgetRowHeight: Number(layoutValue("card7_widget_row_height", 22))
    property int card7ButtonHeight: Number(layoutValue("card7_button_height", 28))
    property int card7WidgetSpacing: Number(layoutValue("card7_widget_spacing", 3))
    property int card7BodyTopMargin: Number(layoutValue("card7_body_top_margin", 2))
    property int card7FeedbackHeight: Number(layoutValue("card7_feedback_height", 34))
    property int card7FeedbackPixelSize: Number(layoutValue("card7_feedback_pixel_size", 9))
    property int card7HeaderSpacing: Number(layoutValue("card7_header_spacing", 2))
    property int card7ContentSpacing: Number(layoutValue("card7_content_spacing", 4))

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
                    guiBridge: root.guiBridge
                    appStateObj: root.appStateObj
                    runtimeSnapshotObj: root.runtimeSnapshotObj
                    sessionStateObj: root.sessionStateObj
                    controlStateObj: root.controlStateObj
                    gameHudObj: root.gameHudObj
                    gameViewObj: root.gameViewObj
                    renderResourcesObj: root.renderResourcesObj
                    designThemeObj: root.designThemeObj
                    gameStyleObj: root.gameStyleObj
                    effectStyleObj: root.effectStyleObj
                    sharedReportActionRaw: root.sharedReportActionRaw
                    sharedSelectedReportSessionId: root.sharedSelectedReportSessionId
                    onReportSelectionChanged: function(sessionId) {
                        if (root.validReportSessionId(sessionId)) root.sharedSelectedReportSessionId = String(sessionId).trim()
                    }
                    onReportActionResultReady: function(raw) { root.acceptReportActionRaw(raw) }
                    widget1Type: root.card1Widget1Type
                    widget1Id: root.card1Widget1Id
                    widget1Label: root.card1Widget1Label
                    widget1Source: root.card1Widget1Source
                    widget1Fallback: root.card1Widget1Fallback
                    widget1Unit: root.card1Widget1Unit
                    widget1ActionId: root.card1Widget1ActionId
                    widget1ArgsJson: root.card1Widget1ArgsJson
                    widget1OptionsText: root.card1Widget1OptionsText
                    widget1Variant: root.card1Widget1Variant
                    widget1Required: root.card1Widget1Required
                    widget1Value: root.card1Widget1Value
                    widget2Type: root.card1Widget2Type
                    widget2Id: root.card1Widget2Id
                    widget2Label: root.card1Widget2Label
                    widget2Source: root.card1Widget2Source
                    widget2Fallback: root.card1Widget2Fallback
                    widget2Unit: root.card1Widget2Unit
                    widget2ActionId: root.card1Widget2ActionId
                    widget2ArgsJson: root.card1Widget2ArgsJson
                    widget2OptionsText: root.card1Widget2OptionsText
                    widget2Variant: root.card1Widget2Variant
                    widget2Required: root.card1Widget2Required
                    widget2Value: root.card1Widget2Value
                    widget3Type: root.card1Widget3Type
                    widget3Id: root.card1Widget3Id
                    widget3Label: root.card1Widget3Label
                    widget3Source: root.card1Widget3Source
                    widget3Fallback: root.card1Widget3Fallback
                    widget3Unit: root.card1Widget3Unit
                    widget3ActionId: root.card1Widget3ActionId
                    widget3ArgsJson: root.card1Widget3ArgsJson
                    widget3OptionsText: root.card1Widget3OptionsText
                    widget3Variant: root.card1Widget3Variant
                    widget3Required: root.card1Widget3Required
                    widget3Value: root.card1Widget3Value
                    widget4Type: root.card1Widget4Type
                    widget4Id: root.card1Widget4Id
                    widget4Label: root.card1Widget4Label
                    widget4Source: root.card1Widget4Source
                    widget4Fallback: root.card1Widget4Fallback
                    widget4Unit: root.card1Widget4Unit
                    widget4ActionId: root.card1Widget4ActionId
                    widget4ArgsJson: root.card1Widget4ArgsJson
                    widget4OptionsText: root.card1Widget4OptionsText
                    widget4Variant: root.card1Widget4Variant
                    widget4Required: root.card1Widget4Required
                    widget4Value: root.card1Widget4Value
                    widget5Type: root.card1Widget5Type
                    widget5Id: root.card1Widget5Id
                    widget5Label: root.card1Widget5Label
                    widget5Source: root.card1Widget5Source
                    widget5Fallback: root.card1Widget5Fallback
                    widget5Unit: root.card1Widget5Unit
                    widget5ActionId: root.card1Widget5ActionId
                    widget5ArgsJson: root.card1Widget5ArgsJson
                    widget5OptionsText: root.card1Widget5OptionsText
                    widget5Variant: root.card1Widget5Variant
                    widget5Required: root.card1Widget5Required
                    widget5Value: root.card1Widget5Value
                    widget6Type: root.card1Widget6Type
                    widget6Id: root.card1Widget6Id
                    widget6Label: root.card1Widget6Label
                    widget6Source: root.card1Widget6Source
                    widget6Fallback: root.card1Widget6Fallback
                    widget6Unit: root.card1Widget6Unit
                    widget6ActionId: root.card1Widget6ActionId
                    widget6ArgsJson: root.card1Widget6ArgsJson
                    widget6OptionsText: root.card1Widget6OptionsText
                    widget6Variant: root.card1Widget6Variant
                    widget6Required: root.card1Widget6Required
                    widget6Value: root.card1Widget6Value
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
                titlePixelSize: root.card1TitlePixelSize
                subtitlePixelSize: root.card1SubtitlePixelSize
                widgetLabelPixelSize: root.card1WidgetLabelPixelSize
                widgetValuePixelSize: root.card1WidgetValuePixelSize
                widgetMetaPixelSize: root.card1WidgetMetaPixelSize
                widgetRowHeight: root.card1WidgetRowHeight
                buttonHeight: root.card1ButtonHeight
                widgetSpacing: root.card1WidgetSpacing
                bodyTopMargin: root.card1BodyTopMargin
                feedbackHeight: root.card1FeedbackHeight
                feedbackPixelSize: root.card1FeedbackPixelSize
                headerSpacing: root.card1HeaderSpacing
                contentSpacing: root.card1ContentSpacing
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
                    guiBridge: root.guiBridge
                    appStateObj: root.appStateObj
                    runtimeSnapshotObj: root.runtimeSnapshotObj
                    sessionStateObj: root.sessionStateObj
                    controlStateObj: root.controlStateObj
                    gameHudObj: root.gameHudObj
                    gameViewObj: root.gameViewObj
                    renderResourcesObj: root.renderResourcesObj
                    designThemeObj: root.designThemeObj
                    gameStyleObj: root.gameStyleObj
                    effectStyleObj: root.effectStyleObj
                    sharedReportActionRaw: root.sharedReportActionRaw
                    sharedSelectedReportSessionId: root.sharedSelectedReportSessionId
                    onReportSelectionChanged: function(sessionId) {
                        if (root.validReportSessionId(sessionId)) root.sharedSelectedReportSessionId = String(sessionId).trim()
                    }
                    onReportActionResultReady: function(raw) { root.acceptReportActionRaw(raw) }
                    widget1Type: root.card2Widget1Type
                    widget1Id: root.card2Widget1Id
                    widget1Label: root.card2Widget1Label
                    widget1Source: root.card2Widget1Source
                    widget1Fallback: root.card2Widget1Fallback
                    widget1Unit: root.card2Widget1Unit
                    widget1ActionId: root.card2Widget1ActionId
                    widget1ArgsJson: root.card2Widget1ArgsJson
                    widget1OptionsText: root.card2Widget1OptionsText
                    widget1Variant: root.card2Widget1Variant
                    widget1Required: root.card2Widget1Required
                    widget1Value: root.card2Widget1Value
                    widget2Type: root.card2Widget2Type
                    widget2Id: root.card2Widget2Id
                    widget2Label: root.card2Widget2Label
                    widget2Source: root.card2Widget2Source
                    widget2Fallback: root.card2Widget2Fallback
                    widget2Unit: root.card2Widget2Unit
                    widget2ActionId: root.card2Widget2ActionId
                    widget2ArgsJson: root.card2Widget2ArgsJson
                    widget2OptionsText: root.card2Widget2OptionsText
                    widget2Variant: root.card2Widget2Variant
                    widget2Required: root.card2Widget2Required
                    widget2Value: root.card2Widget2Value
                    widget3Type: root.card2Widget3Type
                    widget3Id: root.card2Widget3Id
                    widget3Label: root.card2Widget3Label
                    widget3Source: root.card2Widget3Source
                    widget3Fallback: root.card2Widget3Fallback
                    widget3Unit: root.card2Widget3Unit
                    widget3ActionId: root.card2Widget3ActionId
                    widget3ArgsJson: root.card2Widget3ArgsJson
                    widget3OptionsText: root.card2Widget3OptionsText
                    widget3Variant: root.card2Widget3Variant
                    widget3Required: root.card2Widget3Required
                    widget3Value: root.card2Widget3Value
                    widget4Type: root.card2Widget4Type
                    widget4Id: root.card2Widget4Id
                    widget4Label: root.card2Widget4Label
                    widget4Source: root.card2Widget4Source
                    widget4Fallback: root.card2Widget4Fallback
                    widget4Unit: root.card2Widget4Unit
                    widget4ActionId: root.card2Widget4ActionId
                    widget4ArgsJson: root.card2Widget4ArgsJson
                    widget4OptionsText: root.card2Widget4OptionsText
                    widget4Variant: root.card2Widget4Variant
                    widget4Required: root.card2Widget4Required
                    widget4Value: root.card2Widget4Value
                    widget5Type: root.card2Widget5Type
                    widget5Id: root.card2Widget5Id
                    widget5Label: root.card2Widget5Label
                    widget5Source: root.card2Widget5Source
                    widget5Fallback: root.card2Widget5Fallback
                    widget5Unit: root.card2Widget5Unit
                    widget5ActionId: root.card2Widget5ActionId
                    widget5ArgsJson: root.card2Widget5ArgsJson
                    widget5OptionsText: root.card2Widget5OptionsText
                    widget5Variant: root.card2Widget5Variant
                    widget5Required: root.card2Widget5Required
                    widget5Value: root.card2Widget5Value
                    widget6Type: root.card2Widget6Type
                    widget6Id: root.card2Widget6Id
                    widget6Label: root.card2Widget6Label
                    widget6Source: root.card2Widget6Source
                    widget6Fallback: root.card2Widget6Fallback
                    widget6Unit: root.card2Widget6Unit
                    widget6ActionId: root.card2Widget6ActionId
                    widget6ArgsJson: root.card2Widget6ArgsJson
                    widget6OptionsText: root.card2Widget6OptionsText
                    widget6Variant: root.card2Widget6Variant
                    widget6Required: root.card2Widget6Required
                    widget6Value: root.card2Widget6Value
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
                titlePixelSize: root.card2TitlePixelSize
                subtitlePixelSize: root.card2SubtitlePixelSize
                widgetLabelPixelSize: root.card2WidgetLabelPixelSize
                widgetValuePixelSize: root.card2WidgetValuePixelSize
                widgetMetaPixelSize: root.card2WidgetMetaPixelSize
                widgetRowHeight: root.card2WidgetRowHeight
                buttonHeight: root.card2ButtonHeight
                widgetSpacing: root.card2WidgetSpacing
                bodyTopMargin: root.card2BodyTopMargin
                feedbackHeight: root.card2FeedbackHeight
                feedbackPixelSize: root.card2FeedbackPixelSize
                headerSpacing: root.card2HeaderSpacing
                contentSpacing: root.card2ContentSpacing
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
                    guiBridge: root.guiBridge
                    appStateObj: root.appStateObj
                    runtimeSnapshotObj: root.runtimeSnapshotObj
                    sessionStateObj: root.sessionStateObj
                    controlStateObj: root.controlStateObj
                    gameHudObj: root.gameHudObj
                    gameViewObj: root.gameViewObj
                    renderResourcesObj: root.renderResourcesObj
                    designThemeObj: root.designThemeObj
                    gameStyleObj: root.gameStyleObj
                    effectStyleObj: root.effectStyleObj
                    sharedReportActionRaw: root.sharedReportActionRaw
                    sharedSelectedReportSessionId: root.sharedSelectedReportSessionId
                    onReportSelectionChanged: function(sessionId) {
                        if (root.validReportSessionId(sessionId)) root.sharedSelectedReportSessionId = String(sessionId).trim()
                    }
                    onReportActionResultReady: function(raw) { root.acceptReportActionRaw(raw) }
                    widget1Type: root.card3Widget1Type
                    widget1Id: root.card3Widget1Id
                    widget1Label: root.card3Widget1Label
                    widget1Source: root.card3Widget1Source
                    widget1Fallback: root.card3Widget1Fallback
                    widget1Unit: root.card3Widget1Unit
                    widget1ActionId: root.card3Widget1ActionId
                    widget1ArgsJson: root.card3Widget1ArgsJson
                    widget1OptionsText: root.card3Widget1OptionsText
                    widget1Variant: root.card3Widget1Variant
                    widget1Required: root.card3Widget1Required
                    widget1Value: root.card3Widget1Value
                    widget2Type: root.card3Widget2Type
                    widget2Id: root.card3Widget2Id
                    widget2Label: root.card3Widget2Label
                    widget2Source: root.card3Widget2Source
                    widget2Fallback: root.card3Widget2Fallback
                    widget2Unit: root.card3Widget2Unit
                    widget2ActionId: root.card3Widget2ActionId
                    widget2ArgsJson: root.card3Widget2ArgsJson
                    widget2OptionsText: root.card3Widget2OptionsText
                    widget2Variant: root.card3Widget2Variant
                    widget2Required: root.card3Widget2Required
                    widget2Value: root.card3Widget2Value
                    widget3Type: root.card3Widget3Type
                    widget3Id: root.card3Widget3Id
                    widget3Label: root.card3Widget3Label
                    widget3Source: root.card3Widget3Source
                    widget3Fallback: root.card3Widget3Fallback
                    widget3Unit: root.card3Widget3Unit
                    widget3ActionId: root.card3Widget3ActionId
                    widget3ArgsJson: root.card3Widget3ArgsJson
                    widget3OptionsText: root.card3Widget3OptionsText
                    widget3Variant: root.card3Widget3Variant
                    widget3Required: root.card3Widget3Required
                    widget3Value: root.card3Widget3Value
                    widget4Type: root.card3Widget4Type
                    widget4Id: root.card3Widget4Id
                    widget4Label: root.card3Widget4Label
                    widget4Source: root.card3Widget4Source
                    widget4Fallback: root.card3Widget4Fallback
                    widget4Unit: root.card3Widget4Unit
                    widget4ActionId: root.card3Widget4ActionId
                    widget4ArgsJson: root.card3Widget4ArgsJson
                    widget4OptionsText: root.card3Widget4OptionsText
                    widget4Variant: root.card3Widget4Variant
                    widget4Required: root.card3Widget4Required
                    widget4Value: root.card3Widget4Value
                    widget5Type: root.card3Widget5Type
                    widget5Id: root.card3Widget5Id
                    widget5Label: root.card3Widget5Label
                    widget5Source: root.card3Widget5Source
                    widget5Fallback: root.card3Widget5Fallback
                    widget5Unit: root.card3Widget5Unit
                    widget5ActionId: root.card3Widget5ActionId
                    widget5ArgsJson: root.card3Widget5ArgsJson
                    widget5OptionsText: root.card3Widget5OptionsText
                    widget5Variant: root.card3Widget5Variant
                    widget5Required: root.card3Widget5Required
                    widget5Value: root.card3Widget5Value
                    widget6Type: root.card3Widget6Type
                    widget6Id: root.card3Widget6Id
                    widget6Label: root.card3Widget6Label
                    widget6Source: root.card3Widget6Source
                    widget6Fallback: root.card3Widget6Fallback
                    widget6Unit: root.card3Widget6Unit
                    widget6ActionId: root.card3Widget6ActionId
                    widget6ArgsJson: root.card3Widget6ArgsJson
                    widget6OptionsText: root.card3Widget6OptionsText
                    widget6Variant: root.card3Widget6Variant
                    widget6Required: root.card3Widget6Required
                    widget6Value: root.card3Widget6Value
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
                titlePixelSize: root.card3TitlePixelSize
                subtitlePixelSize: root.card3SubtitlePixelSize
                widgetLabelPixelSize: root.card3WidgetLabelPixelSize
                widgetValuePixelSize: root.card3WidgetValuePixelSize
                widgetMetaPixelSize: root.card3WidgetMetaPixelSize
                widgetRowHeight: root.card3WidgetRowHeight
                buttonHeight: root.card3ButtonHeight
                widgetSpacing: root.card3WidgetSpacing
                bodyTopMargin: root.card3BodyTopMargin
                feedbackHeight: root.card3FeedbackHeight
                feedbackPixelSize: root.card3FeedbackPixelSize
                headerSpacing: root.card3HeaderSpacing
                contentSpacing: root.card3ContentSpacing
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
                    guiBridge: root.guiBridge
                    appStateObj: root.appStateObj
                    runtimeSnapshotObj: root.runtimeSnapshotObj
                    sessionStateObj: root.sessionStateObj
                    controlStateObj: root.controlStateObj
                    gameHudObj: root.gameHudObj
                    gameViewObj: root.gameViewObj
                    renderResourcesObj: root.renderResourcesObj
                    designThemeObj: root.designThemeObj
                    gameStyleObj: root.gameStyleObj
                    effectStyleObj: root.effectStyleObj
                    sharedReportActionRaw: root.sharedReportActionRaw
                    sharedSelectedReportSessionId: root.sharedSelectedReportSessionId
                    onReportSelectionChanged: function(sessionId) {
                        if (root.validReportSessionId(sessionId)) root.sharedSelectedReportSessionId = String(sessionId).trim()
                    }
                    onReportActionResultReady: function(raw) { root.acceptReportActionRaw(raw) }
                    widget1Type: root.card4Widget1Type
                    widget1Id: root.card4Widget1Id
                    widget1Label: root.card4Widget1Label
                    widget1Source: root.card4Widget1Source
                    widget1Fallback: root.card4Widget1Fallback
                    widget1Unit: root.card4Widget1Unit
                    widget1ActionId: root.card4Widget1ActionId
                    widget1ArgsJson: root.card4Widget1ArgsJson
                    widget1OptionsText: root.card4Widget1OptionsText
                    widget1Variant: root.card4Widget1Variant
                    widget1Required: root.card4Widget1Required
                    widget1Value: root.card4Widget1Value
                    widget2Type: root.card4Widget2Type
                    widget2Id: root.card4Widget2Id
                    widget2Label: root.card4Widget2Label
                    widget2Source: root.card4Widget2Source
                    widget2Fallback: root.card4Widget2Fallback
                    widget2Unit: root.card4Widget2Unit
                    widget2ActionId: root.card4Widget2ActionId
                    widget2ArgsJson: root.card4Widget2ArgsJson
                    widget2OptionsText: root.card4Widget2OptionsText
                    widget2Variant: root.card4Widget2Variant
                    widget2Required: root.card4Widget2Required
                    widget2Value: root.card4Widget2Value
                    widget3Type: root.card4Widget3Type
                    widget3Id: root.card4Widget3Id
                    widget3Label: root.card4Widget3Label
                    widget3Source: root.card4Widget3Source
                    widget3Fallback: root.card4Widget3Fallback
                    widget3Unit: root.card4Widget3Unit
                    widget3ActionId: root.card4Widget3ActionId
                    widget3ArgsJson: root.card4Widget3ArgsJson
                    widget3OptionsText: root.card4Widget3OptionsText
                    widget3Variant: root.card4Widget3Variant
                    widget3Required: root.card4Widget3Required
                    widget3Value: root.card4Widget3Value
                    widget4Type: root.card4Widget4Type
                    widget4Id: root.card4Widget4Id
                    widget4Label: root.card4Widget4Label
                    widget4Source: root.card4Widget4Source
                    widget4Fallback: root.card4Widget4Fallback
                    widget4Unit: root.card4Widget4Unit
                    widget4ActionId: root.card4Widget4ActionId
                    widget4ArgsJson: root.card4Widget4ArgsJson
                    widget4OptionsText: root.card4Widget4OptionsText
                    widget4Variant: root.card4Widget4Variant
                    widget4Required: root.card4Widget4Required
                    widget4Value: root.card4Widget4Value
                    widget5Type: root.card4Widget5Type
                    widget5Id: root.card4Widget5Id
                    widget5Label: root.card4Widget5Label
                    widget5Source: root.card4Widget5Source
                    widget5Fallback: root.card4Widget5Fallback
                    widget5Unit: root.card4Widget5Unit
                    widget5ActionId: root.card4Widget5ActionId
                    widget5ArgsJson: root.card4Widget5ArgsJson
                    widget5OptionsText: root.card4Widget5OptionsText
                    widget5Variant: root.card4Widget5Variant
                    widget5Required: root.card4Widget5Required
                    widget5Value: root.card4Widget5Value
                    widget6Type: root.card4Widget6Type
                    widget6Id: root.card4Widget6Id
                    widget6Label: root.card4Widget6Label
                    widget6Source: root.card4Widget6Source
                    widget6Fallback: root.card4Widget6Fallback
                    widget6Unit: root.card4Widget6Unit
                    widget6ActionId: root.card4Widget6ActionId
                    widget6ArgsJson: root.card4Widget6ArgsJson
                    widget6OptionsText: root.card4Widget6OptionsText
                    widget6Variant: root.card4Widget6Variant
                    widget6Required: root.card4Widget6Required
                    widget6Value: root.card4Widget6Value
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
                titlePixelSize: root.card4TitlePixelSize
                subtitlePixelSize: root.card4SubtitlePixelSize
                widgetLabelPixelSize: root.card4WidgetLabelPixelSize
                widgetValuePixelSize: root.card4WidgetValuePixelSize
                widgetMetaPixelSize: root.card4WidgetMetaPixelSize
                widgetRowHeight: root.card4WidgetRowHeight
                buttonHeight: root.card4ButtonHeight
                widgetSpacing: root.card4WidgetSpacing
                bodyTopMargin: root.card4BodyTopMargin
                feedbackHeight: root.card4FeedbackHeight
                feedbackPixelSize: root.card4FeedbackPixelSize
                headerSpacing: root.card4HeaderSpacing
                contentSpacing: root.card4ContentSpacing
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
                    guiBridge: root.guiBridge
                    appStateObj: root.appStateObj
                    runtimeSnapshotObj: root.runtimeSnapshotObj
                    sessionStateObj: root.sessionStateObj
                    controlStateObj: root.controlStateObj
                    gameHudObj: root.gameHudObj
                    gameViewObj: root.gameViewObj
                    renderResourcesObj: root.renderResourcesObj
                    designThemeObj: root.designThemeObj
                    gameStyleObj: root.gameStyleObj
                    effectStyleObj: root.effectStyleObj
                    sharedReportActionRaw: root.sharedReportActionRaw
                    sharedSelectedReportSessionId: root.sharedSelectedReportSessionId
                    onReportSelectionChanged: function(sessionId) {
                        if (root.validReportSessionId(sessionId)) root.sharedSelectedReportSessionId = String(sessionId).trim()
                    }
                    onReportActionResultReady: function(raw) { root.acceptReportActionRaw(raw) }
                    widget1Type: root.card5Widget1Type
                    widget1Id: root.card5Widget1Id
                    widget1Label: root.card5Widget1Label
                    widget1Source: root.card5Widget1Source
                    widget1Fallback: root.card5Widget1Fallback
                    widget1Unit: root.card5Widget1Unit
                    widget1ActionId: root.card5Widget1ActionId
                    widget1ArgsJson: root.card5Widget1ArgsJson
                    widget1OptionsText: root.card5Widget1OptionsText
                    widget1Variant: root.card5Widget1Variant
                    widget1Required: root.card5Widget1Required
                    widget1Value: root.card5Widget1Value
                    widget2Type: root.card5Widget2Type
                    widget2Id: root.card5Widget2Id
                    widget2Label: root.card5Widget2Label
                    widget2Source: root.card5Widget2Source
                    widget2Fallback: root.card5Widget2Fallback
                    widget2Unit: root.card5Widget2Unit
                    widget2ActionId: root.card5Widget2ActionId
                    widget2ArgsJson: root.card5Widget2ArgsJson
                    widget2OptionsText: root.card5Widget2OptionsText
                    widget2Variant: root.card5Widget2Variant
                    widget2Required: root.card5Widget2Required
                    widget2Value: root.card5Widget2Value
                    widget3Type: root.card5Widget3Type
                    widget3Id: root.card5Widget3Id
                    widget3Label: root.card5Widget3Label
                    widget3Source: root.card5Widget3Source
                    widget3Fallback: root.card5Widget3Fallback
                    widget3Unit: root.card5Widget3Unit
                    widget3ActionId: root.card5Widget3ActionId
                    widget3ArgsJson: root.card5Widget3ArgsJson
                    widget3OptionsText: root.card5Widget3OptionsText
                    widget3Variant: root.card5Widget3Variant
                    widget3Required: root.card5Widget3Required
                    widget3Value: root.card5Widget3Value
                    widget4Type: root.card5Widget4Type
                    widget4Id: root.card5Widget4Id
                    widget4Label: root.card5Widget4Label
                    widget4Source: root.card5Widget4Source
                    widget4Fallback: root.card5Widget4Fallback
                    widget4Unit: root.card5Widget4Unit
                    widget4ActionId: root.card5Widget4ActionId
                    widget4ArgsJson: root.card5Widget4ArgsJson
                    widget4OptionsText: root.card5Widget4OptionsText
                    widget4Variant: root.card5Widget4Variant
                    widget4Required: root.card5Widget4Required
                    widget4Value: root.card5Widget4Value
                    widget5Type: root.card5Widget5Type
                    widget5Id: root.card5Widget5Id
                    widget5Label: root.card5Widget5Label
                    widget5Source: root.card5Widget5Source
                    widget5Fallback: root.card5Widget5Fallback
                    widget5Unit: root.card5Widget5Unit
                    widget5ActionId: root.card5Widget5ActionId
                    widget5ArgsJson: root.card5Widget5ArgsJson
                    widget5OptionsText: root.card5Widget5OptionsText
                    widget5Variant: root.card5Widget5Variant
                    widget5Required: root.card5Widget5Required
                    widget5Value: root.card5Widget5Value
                    widget6Type: root.card5Widget6Type
                    widget6Id: root.card5Widget6Id
                    widget6Label: root.card5Widget6Label
                    widget6Source: root.card5Widget6Source
                    widget6Fallback: root.card5Widget6Fallback
                    widget6Unit: root.card5Widget6Unit
                    widget6ActionId: root.card5Widget6ActionId
                    widget6ArgsJson: root.card5Widget6ArgsJson
                    widget6OptionsText: root.card5Widget6OptionsText
                    widget6Variant: root.card5Widget6Variant
                    widget6Required: root.card5Widget6Required
                    widget6Value: root.card5Widget6Value
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
                titlePixelSize: root.card5TitlePixelSize
                subtitlePixelSize: root.card5SubtitlePixelSize
                widgetLabelPixelSize: root.card5WidgetLabelPixelSize
                widgetValuePixelSize: root.card5WidgetValuePixelSize
                widgetMetaPixelSize: root.card5WidgetMetaPixelSize
                widgetRowHeight: root.card5WidgetRowHeight
                buttonHeight: root.card5ButtonHeight
                widgetSpacing: root.card5WidgetSpacing
                bodyTopMargin: root.card5BodyTopMargin
                feedbackHeight: root.card5FeedbackHeight
                feedbackPixelSize: root.card5FeedbackPixelSize
                headerSpacing: root.card5HeaderSpacing
                contentSpacing: root.card5ContentSpacing
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
                    guiBridge: root.guiBridge
                    appStateObj: root.appStateObj
                    runtimeSnapshotObj: root.runtimeSnapshotObj
                    sessionStateObj: root.sessionStateObj
                    controlStateObj: root.controlStateObj
                    gameHudObj: root.gameHudObj
                    gameViewObj: root.gameViewObj
                    renderResourcesObj: root.renderResourcesObj
                    designThemeObj: root.designThemeObj
                    gameStyleObj: root.gameStyleObj
                    effectStyleObj: root.effectStyleObj
                    sharedReportActionRaw: root.sharedReportActionRaw
                    sharedSelectedReportSessionId: root.sharedSelectedReportSessionId
                    onReportSelectionChanged: function(sessionId) {
                        if (root.validReportSessionId(sessionId)) root.sharedSelectedReportSessionId = String(sessionId).trim()
                    }
                    onReportActionResultReady: function(raw) { root.acceptReportActionRaw(raw) }
                    widget1Type: root.card6Widget1Type
                    widget1Id: root.card6Widget1Id
                    widget1Label: root.card6Widget1Label
                    widget1Source: root.card6Widget1Source
                    widget1Fallback: root.card6Widget1Fallback
                    widget1Unit: root.card6Widget1Unit
                    widget1ActionId: root.card6Widget1ActionId
                    widget1ArgsJson: root.card6Widget1ArgsJson
                    widget1OptionsText: root.card6Widget1OptionsText
                    widget1Variant: root.card6Widget1Variant
                    widget1Required: root.card6Widget1Required
                    widget1Value: root.card6Widget1Value
                    widget2Type: root.card6Widget2Type
                    widget2Id: root.card6Widget2Id
                    widget2Label: root.card6Widget2Label
                    widget2Source: root.card6Widget2Source
                    widget2Fallback: root.card6Widget2Fallback
                    widget2Unit: root.card6Widget2Unit
                    widget2ActionId: root.card6Widget2ActionId
                    widget2ArgsJson: root.card6Widget2ArgsJson
                    widget2OptionsText: root.card6Widget2OptionsText
                    widget2Variant: root.card6Widget2Variant
                    widget2Required: root.card6Widget2Required
                    widget2Value: root.card6Widget2Value
                    widget3Type: root.card6Widget3Type
                    widget3Id: root.card6Widget3Id
                    widget3Label: root.card6Widget3Label
                    widget3Source: root.card6Widget3Source
                    widget3Fallback: root.card6Widget3Fallback
                    widget3Unit: root.card6Widget3Unit
                    widget3ActionId: root.card6Widget3ActionId
                    widget3ArgsJson: root.card6Widget3ArgsJson
                    widget3OptionsText: root.card6Widget3OptionsText
                    widget3Variant: root.card6Widget3Variant
                    widget3Required: root.card6Widget3Required
                    widget3Value: root.card6Widget3Value
                    widget4Type: root.card6Widget4Type
                    widget4Id: root.card6Widget4Id
                    widget4Label: root.card6Widget4Label
                    widget4Source: root.card6Widget4Source
                    widget4Fallback: root.card6Widget4Fallback
                    widget4Unit: root.card6Widget4Unit
                    widget4ActionId: root.card6Widget4ActionId
                    widget4ArgsJson: root.card6Widget4ArgsJson
                    widget4OptionsText: root.card6Widget4OptionsText
                    widget4Variant: root.card6Widget4Variant
                    widget4Required: root.card6Widget4Required
                    widget4Value: root.card6Widget4Value
                    widget5Type: root.card6Widget5Type
                    widget5Id: root.card6Widget5Id
                    widget5Label: root.card6Widget5Label
                    widget5Source: root.card6Widget5Source
                    widget5Fallback: root.card6Widget5Fallback
                    widget5Unit: root.card6Widget5Unit
                    widget5ActionId: root.card6Widget5ActionId
                    widget5ArgsJson: root.card6Widget5ArgsJson
                    widget5OptionsText: root.card6Widget5OptionsText
                    widget5Variant: root.card6Widget5Variant
                    widget5Required: root.card6Widget5Required
                    widget5Value: root.card6Widget5Value
                    widget6Type: root.card6Widget6Type
                    widget6Id: root.card6Widget6Id
                    widget6Label: root.card6Widget6Label
                    widget6Source: root.card6Widget6Source
                    widget6Fallback: root.card6Widget6Fallback
                    widget6Unit: root.card6Widget6Unit
                    widget6ActionId: root.card6Widget6ActionId
                    widget6ArgsJson: root.card6Widget6ArgsJson
                    widget6OptionsText: root.card6Widget6OptionsText
                    widget6Variant: root.card6Widget6Variant
                    widget6Required: root.card6Widget6Required
                    widget6Value: root.card6Widget6Value
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
                titlePixelSize: root.card6TitlePixelSize
                subtitlePixelSize: root.card6SubtitlePixelSize
                widgetLabelPixelSize: root.card6WidgetLabelPixelSize
                widgetValuePixelSize: root.card6WidgetValuePixelSize
                widgetMetaPixelSize: root.card6WidgetMetaPixelSize
                widgetRowHeight: root.card6WidgetRowHeight
                buttonHeight: root.card6ButtonHeight
                widgetSpacing: root.card6WidgetSpacing
                bodyTopMargin: root.card6BodyTopMargin
                feedbackHeight: root.card6FeedbackHeight
                feedbackPixelSize: root.card6FeedbackPixelSize
                headerSpacing: root.card6HeaderSpacing
                contentSpacing: root.card6ContentSpacing
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
                    guiBridge: root.guiBridge
                    appStateObj: root.appStateObj
                    runtimeSnapshotObj: root.runtimeSnapshotObj
                    sessionStateObj: root.sessionStateObj
                    controlStateObj: root.controlStateObj
                    gameHudObj: root.gameHudObj
                    gameViewObj: root.gameViewObj
                    renderResourcesObj: root.renderResourcesObj
                    designThemeObj: root.designThemeObj
                    gameStyleObj: root.gameStyleObj
                    effectStyleObj: root.effectStyleObj
                    sharedReportActionRaw: root.sharedReportActionRaw
                    sharedSelectedReportSessionId: root.sharedSelectedReportSessionId
                    onReportSelectionChanged: function(sessionId) {
                        if (root.validReportSessionId(sessionId)) root.sharedSelectedReportSessionId = String(sessionId).trim()
                    }
                    onReportActionResultReady: function(raw) { root.acceptReportActionRaw(raw) }
                    widget1Type: root.card7Widget1Type
                    widget1Id: root.card7Widget1Id
                    widget1Label: root.card7Widget1Label
                    widget1Source: root.card7Widget1Source
                    widget1Fallback: root.card7Widget1Fallback
                    widget1Unit: root.card7Widget1Unit
                    widget1ActionId: root.card7Widget1ActionId
                    widget1ArgsJson: root.card7Widget1ArgsJson
                    widget1OptionsText: root.card7Widget1OptionsText
                    widget1Variant: root.card7Widget1Variant
                    widget1Required: root.card7Widget1Required
                    widget1Value: root.card7Widget1Value
                    widget2Type: root.card7Widget2Type
                    widget2Id: root.card7Widget2Id
                    widget2Label: root.card7Widget2Label
                    widget2Source: root.card7Widget2Source
                    widget2Fallback: root.card7Widget2Fallback
                    widget2Unit: root.card7Widget2Unit
                    widget2ActionId: root.card7Widget2ActionId
                    widget2ArgsJson: root.card7Widget2ArgsJson
                    widget2OptionsText: root.card7Widget2OptionsText
                    widget2Variant: root.card7Widget2Variant
                    widget2Required: root.card7Widget2Required
                    widget2Value: root.card7Widget2Value
                    widget3Type: root.card7Widget3Type
                    widget3Id: root.card7Widget3Id
                    widget3Label: root.card7Widget3Label
                    widget3Source: root.card7Widget3Source
                    widget3Fallback: root.card7Widget3Fallback
                    widget3Unit: root.card7Widget3Unit
                    widget3ActionId: root.card7Widget3ActionId
                    widget3ArgsJson: root.card7Widget3ArgsJson
                    widget3OptionsText: root.card7Widget3OptionsText
                    widget3Variant: root.card7Widget3Variant
                    widget3Required: root.card7Widget3Required
                    widget3Value: root.card7Widget3Value
                    widget4Type: root.card7Widget4Type
                    widget4Id: root.card7Widget4Id
                    widget4Label: root.card7Widget4Label
                    widget4Source: root.card7Widget4Source
                    widget4Fallback: root.card7Widget4Fallback
                    widget4Unit: root.card7Widget4Unit
                    widget4ActionId: root.card7Widget4ActionId
                    widget4ArgsJson: root.card7Widget4ArgsJson
                    widget4OptionsText: root.card7Widget4OptionsText
                    widget4Variant: root.card7Widget4Variant
                    widget4Required: root.card7Widget4Required
                    widget4Value: root.card7Widget4Value
                    widget5Type: root.card7Widget5Type
                    widget5Id: root.card7Widget5Id
                    widget5Label: root.card7Widget5Label
                    widget5Source: root.card7Widget5Source
                    widget5Fallback: root.card7Widget5Fallback
                    widget5Unit: root.card7Widget5Unit
                    widget5ActionId: root.card7Widget5ActionId
                    widget5ArgsJson: root.card7Widget5ArgsJson
                    widget5OptionsText: root.card7Widget5OptionsText
                    widget5Variant: root.card7Widget5Variant
                    widget5Required: root.card7Widget5Required
                    widget5Value: root.card7Widget5Value
                    widget6Type: root.card7Widget6Type
                    widget6Id: root.card7Widget6Id
                    widget6Label: root.card7Widget6Label
                    widget6Source: root.card7Widget6Source
                    widget6Fallback: root.card7Widget6Fallback
                    widget6Unit: root.card7Widget6Unit
                    widget6ActionId: root.card7Widget6ActionId
                    widget6ArgsJson: root.card7Widget6ArgsJson
                    widget6OptionsText: root.card7Widget6OptionsText
                    widget6Variant: root.card7Widget6Variant
                    widget6Required: root.card7Widget6Required
                    widget6Value: root.card7Widget6Value
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
                titlePixelSize: root.card7TitlePixelSize
                subtitlePixelSize: root.card7SubtitlePixelSize
                widgetLabelPixelSize: root.card7WidgetLabelPixelSize
                widgetValuePixelSize: root.card7WidgetValuePixelSize
                widgetMetaPixelSize: root.card7WidgetMetaPixelSize
                widgetRowHeight: root.card7WidgetRowHeight
                buttonHeight: root.card7ButtonHeight
                widgetSpacing: root.card7WidgetSpacing
                bodyTopMargin: root.card7BodyTopMargin
                feedbackHeight: root.card7FeedbackHeight
                feedbackPixelSize: root.card7FeedbackPixelSize
                headerSpacing: root.card7HeaderSpacing
                contentSpacing: root.card7ContentSpacing
                }
            }
        }
    }
}
