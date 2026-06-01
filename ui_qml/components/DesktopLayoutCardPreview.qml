import QtQuick 2.15
import QtQuick.Controls 2.15

// Select widgets are rendered by ConfigSelectWidget (Basic.ComboBox) for rounded card-style popups.

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
    property var designThemeObj: ({})
    property var gameStyleObj: ({})
    property var effectStyleObj: ({})
    property string sharedReportActionRaw: ""
    property string sharedSelectedReportSessionId: ""
    signal reportActionResultReady(string raw)
    signal reportSelectionChanged(string sessionId)

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

    property string widget1Type: ""; property string widget1Id: ""; property string widget1Label: ""; property string widget1Source: ""; property string widget1Fallback: ""; property string widget1Unit: ""; property string widget1ActionId: ""; property string widget1ArgsJson: "{}"; property string widget1OptionsText: ""; property string widget1Variant: ""; property bool widget1Required: false; property string widget1Value: ""; property string widget1InputText: ""; property string widget1SelectText: ""
    property string widget2Type: ""; property string widget2Id: ""; property string widget2Label: ""; property string widget2Source: ""; property string widget2Fallback: ""; property string widget2Unit: ""; property string widget2ActionId: ""; property string widget2ArgsJson: "{}"; property string widget2OptionsText: ""; property string widget2Variant: ""; property bool widget2Required: false; property string widget2Value: ""; property string widget2InputText: ""; property string widget2SelectText: ""
    property string widget3Type: ""; property string widget3Id: ""; property string widget3Label: ""; property string widget3Source: ""; property string widget3Fallback: ""; property string widget3Unit: ""; property string widget3ActionId: ""; property string widget3ArgsJson: "{}"; property string widget3OptionsText: ""; property string widget3Variant: ""; property bool widget3Required: false; property string widget3Value: ""; property string widget3InputText: ""; property string widget3SelectText: ""
    property string widget4Type: ""; property string widget4Id: ""; property string widget4Label: ""; property string widget4Source: ""; property string widget4Fallback: ""; property string widget4Unit: ""; property string widget4ActionId: ""; property string widget4ArgsJson: "{}"; property string widget4OptionsText: ""; property string widget4Variant: ""; property bool widget4Required: false; property string widget4Value: ""; property string widget4InputText: ""; property string widget4SelectText: ""
    property string widget5Type: ""; property string widget5Id: ""; property string widget5Label: ""; property string widget5Source: ""; property string widget5Fallback: ""; property string widget5Unit: ""; property string widget5ActionId: ""; property string widget5ArgsJson: "{}"; property string widget5OptionsText: ""; property string widget5Variant: ""; property bool widget5Required: false; property string widget5Value: ""; property string widget5InputText: ""; property string widget5SelectText: ""
    property string widget6Type: ""; property string widget6Id: ""; property string widget6Label: ""; property string widget6Source: ""; property string widget6Fallback: ""; property string widget6Unit: ""; property string widget6ActionId: ""; property string widget6ArgsJson: "{}"; property string widget6OptionsText: ""; property string widget6Variant: ""; property bool widget6Required: false; property string widget6Value: ""; property string widget6InputText: ""; property string widget6SelectText: ""

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

    // Typography / layout knobs for card readability. These are driven by card style fields.
    property int compactLabelPixelSize: 10
    property int compactValuePixelSize: 12
    property int compactMetaPixelSize: 9
    property int compactRowHeight: 22
    property int compactButtonHeight: 28
    property int compactWidgetSpacing: 3
    property int compactBodyTopMargin: 2

    property int titlePixelSize: 15
    property int subtitlePixelSize: 10
    property int widgetLabelPixelSize: compactLabelPixelSize
    property int widgetValuePixelSize: compactValuePixelSize
    property int widgetMetaPixelSize: compactMetaPixelSize
    property int widgetRowHeight: compactRowHeight
    property int buttonHeight: compactButtonHeight
    property int widgetSpacing: compactWidgetSpacing
    property int bodyTopMargin: compactBodyTopMargin
    property int feedbackHeight: 34
    property int feedbackPixelSize: compactMetaPixelSize
    property int headerSpacing: 2
    property int contentSpacing: 4

    property string lastDesktopActionId: ""
    property string lastDesktopActionStatus: ""
    property string lastDesktopActionMessage: ""
    property string lastDesktopActionRaw: ""
    property string lastProfileActionRaw: ""
    property string lastCalibrationActionRaw: ""
    property string lastReportActionRaw: ""

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

    function compactJson(value, fallbackValue) {
        if (value === undefined || value === null || value === "") {
            return safeText(fallbackValue, "n/a")
        }
        if (typeof value === "string") {
            return value
        }
        try {
            return JSON.stringify(value)
        } catch (e) {
            return String(value)
        }
    }

    function sourceRootObject(rootName) {
        if (rootName === "appState") return root.appStateObj
        if (rootName === "runtimeSnapshot") return root.runtimeSnapshotObj
        if (rootName === "sessionState") return root.sessionStateObj
        if (rootName === "controlState" || rootName === "controlStateJson") return root.controlStateObj
        if (rootName === "gameHud" || rootName === "gameHudJson") return root.gameHudObj
        if (rootName === "gameView" || rootName === "gameViewJson") return root.gameViewObj
        if (rootName === "renderResources" || rootName === "renderResourcesJson") return root.renderResourcesObj
        return null
    }

    function sourceValue(source, fallbackValue) {
        if (!source || source === "") return safeText(fallbackValue, "n/a")
        if (source === "gameHudJson" || source === "gameHud" || source === "gameViewJson" || source === "gameView") {
            return compactJson(sourceRootObject(source), fallbackValue)
        }
        var dot = source.indexOf(".")
        if (dot < 1) {
            return safeText(fallbackValue, "n/a")
        }
        var rootName = source.slice(0, dot)
        var fieldName = source.slice(dot + 1)
        var obj = sourceRootObject(rootName)
        if (!obj || fieldName.length === 0) {
            return safeText(fallbackValue, "n/a")
        }
        return safeText(obj[fieldName], fallbackValue)
    }

    function widgetDisplayText(type, label, source, fallback, unit, value, widgetId) {
        if (type === "input") return safeText(fallback, "")
        if (type === "select") return safeText(value, fallback)
        if (safeText(widgetId, "") === "current_selected_session_id") {
            var shared = safeText(root.sharedSelectedReportSessionId, "").trim()
            if (isValidReportSessionText(shared)) return shared
        }
        var reportKey = reportKeyFromWidget(widgetId, source, label)
        if (reportKey.length > 0) {
            var stateFallback = sourceValue(source, fallback)
            if (reportKey === "report_path") return reportValue("report_path", reportValue("latest_report_path", stateFallback))
            if (reportKey === "latest_report_path") return reportValue("latest_report_path", reportValue("report_path", stateFallback))
            if (reportKey === "export_path") return reportExportPathValue("n/a")
            if (reportKey === "report_list_text") return reportListText(stateFallback)
            if (reportKey === "session_id") return reportValue("session_id", reportValue("latest_session_id", stateFallback))
            if (reportKey === "report_preview_available") {
                var previewText = reportValue("report_preview", "")
                if (previewText.length > 0 && previewText !== "n/a") return "true"
                return reportValue("report_preview_available", stateFallback)
            }
            return reportValue(reportKey, stateFallback)
        }
        var resolved = value && value.length > 0 ? value : sourceValue(source, fallback)
        var unitText = unit && unit.length > 0 && resolved !== fallback ? " " + unit : ""
        return safeText(resolved, fallback) + unitText
    }

    function widgetVisible(type, idx) {
        return idx <= root.widgetCount && type.length > 0
    }

    function isGameCanvasCard() {
        return root.cardId === "game_canvas_card"
                || root.roleText === "game_canvas"
                || root.roleText === "game_canvas_live"
                || root.roleText === "live_game_canvas"
                || root.cardType === "game_canvas"
    }

    function isHudOverlayCard() {
        return root.cardId === "game_hud_card"
                || root.cardId === "game_hud_overlay_card"
                || root.roleText === "hud_overlay"
                || root.cardType === "hud_overlay"
    }

    function rowHeightFor(type) {
        if (type === "button" || type === "input" || type === "select") return root.buttonHeight
        if (type === "text") return Math.max(root.widgetRowHeight * 3, root.buttonHeight * 3)
        return root.widgetRowHeight
    }

    function reportListPanelVisible() {
        if (root.cardId !== "report_detail_card") return false
        var obj = currentReportRawObject()
        if (reportActionIdFromObject(obj) !== "report.list") return false
        var text = reportListText("")
        return text.length > 0 && text !== "n/a" && text.indexOf("Click Refresh Report List") < 0
    }

    function reportListPanelText() {
        return reportListText("No reports found for current user.")
    }

    function isReportPathKey(key) {
        var text = safeText(key, "").toLowerCase()
        return text.indexOf("path") >= 0 || text.indexOf("preview") >= 0
    }

    function buttonLabel(label, actionId, required) {
        var base = label && label.length > 0 ? label : actionId
        if (required) return base + " *"
        return base
    }

    function optionsFromText(optionsText, fallbackText) {
        var raw = optionsText && optionsText.length > 0 ? optionsText : fallbackText
        if (!raw || raw.length === 0) return ["TEST", "demo"]
        var parts = String(raw).split("|")
        var out = []
        for (var i = 0; i < parts.length; i += 1) {
            var item = String(parts[i]).trim()
            if (item.length > 0) out.push(item)
        }
        return out.length > 0 ? out : ["TEST", "demo"]
    }

    function jsonEscapeText(value) {
        return safeText(value, "").replace(/\\/g, "\\\\").replace(/"/g, "\\\"")
    }

    function replaceAllText(text, needle, value) {
        return String(text).split(needle).join(value)
    }

    function isReportAction(actionId) {
        return safeText(actionId, "").indexOf("report.") === 0
    }

    function reportKeyFromWidget(widgetId, source, label) {
        var idText = safeText(widgetId, "").toLowerCase()
        var sourceText = safeText(source, "").toLowerCase()
        var labelText = safeText(label, "").toLowerCase()
        var combined = idText + " " + sourceText + " " + labelText
        if (idText === "selected_report_path" || idText === "popup_current_path" || sourceText.indexOf("report_selected_report_path") >= 0) return "report_path"
        if (idText === "latest_report_path" || sourceText.indexOf("latest_report_path") >= 0) return "latest_report_path"
        if (idText === "export_path" || sourceText.indexOf("report_export_path") >= 0) return "export_path"
        if (idText === "popup_preview_text" || sourceText.indexOf("report_selected_report_preview") >= 0 || sourceText.indexOf("report_preview") >= 0) return "report_preview"
        if (idText === "report_list_text" || sourceText.indexOf("report_list_text") >= 0 || combined.indexOf("current user reports") >= 0) return "report_list_text"
        if (idText === "selected_session_id" || idText === "current_selected_session_id" || sourceText.indexOf("report_selected_session_id") >= 0) return "session_id"
        if (idText === "selected_report_user" || sourceText.indexOf("report_selected_user_id") >= 0) return "user_id"
        if (idText === "report_available" || sourceText.indexOf("report_available") >= 0) return "report_available"
        if (idText === "preview_loaded" || idText === "report_preview_available" || sourceText.indexOf("report_preview_available") >= 0) return "report_preview_available"
        if (combined.indexOf("report path") >= 0) return "report_path"
        if (combined.indexOf("export path") >= 0) return "export_path"
        if (combined.indexOf("preview") >= 0 && combined.indexOf("report") >= 0) return "report_preview"
        return ""
    }

    function reportListOptionsFromObject(obj, depth) {
        if (!obj || depth <= 0) return []
        var out = []
        function addCandidate(value) {
            var text = safeText(value, "").trim()
            if (text.length === 0 || text === "n/a" || text === "no_report_available") return
            if (out.indexOf(text) < 0) out.push(text)
        }
        function scanArray(arr) {
            if (!arr || !Array.isArray(arr)) return
            for (var i = 0; i < arr.length; i++) {
                var item = arr[i]
                if (item && typeof item === "object") {
                    var available = item.report_available
                    var pathText = safeText(item.report_path || item.latest_report_path || item.source_report_path || "", "")
                    // Report selector must prefer actual report records.  A current-user
                    // session without report_path was the reason Show Selected kept
                    // opening a no-preview/no-path result after switching users.
                    if (available === false || pathText.length === 0 || pathText === "n/a" || pathText === "null") {
                        continue
                    }
                    addCandidate(item.session_id || item.report_id || item.id)
                } else {
                    addCandidate(item)
                }
            }
        }
        scanArray(obj.items)
        scanArray(obj.sessions)
        var priority = ["result", "detail", "report", "summary"]
        for (var p = 0; p < priority.length; p++) {
            var name = priority[p]
            if (obj[name] && typeof obj[name] === "object") {
                var nested = reportListOptionsFromObject(obj[name], depth - 1)
                for (var n = 0; n < nested.length; n++) addCandidate(nested[n])
            }
        }
        return out
    }

    function reportSelectorOptionsText(staticOptionsText) {
        var raw = root.lastReportActionRaw.length > 0 ? root.lastReportActionRaw : (root.sharedReportActionRaw.length > 0 ? root.sharedReportActionRaw : root.lastDesktopActionRaw)
        try {
            var obj = JSON.parse(raw || "{}")
            var options = reportListOptionsFromObject(obj, 4)
            if (options.length > 0) return options.join("|")
        } catch (e) {
        }
        var contextOptions = reportContextValue("report_options_text", "")
        if (contextOptions.length > 0 && contextOptions !== "n/a") return contextOptions
        return staticOptionsText
    }

    function isValidReportSessionText(value) {
        var text = safeText(value, "").trim()
        return text.length > 0 && text !== "n/a" && text !== "no_report_available" && text !== "manual" && text !== "null"
    }

    function rememberReportSelection(value) {
        var text = safeText(value, "").trim()
        if (isValidReportSessionText(text) && text !== root.sharedSelectedReportSessionId) {
            root.reportSelectionChanged(text)
        }
    }

    function reportPrimarySessionId(fallbackValue) {
        var shared = safeText(root.sharedSelectedReportSessionId, "").trim()
        if (isValidReportSessionText(shared)) return shared
        var fromRaw = reportValue("session_id", reportValue("latest_session_id", ""))
        if (isValidReportSessionText(fromRaw)) return fromRaw
        var fromState = sourceValue("controlStateJson.report_selected_session_id", sourceValue("controlStateJson.latest_session_id", fallbackValue))
        if (isValidReportSessionText(fromState)) return fromState
        return safeText(fallbackValue, "")
    }

    function sanitizeReportPayloadText(actionId, payloadText, widgetId) {
        if (!isReportAction(actionId)) return payloadText
        var obj = ({})
        try {
            obj = JSON.parse(payloadText && payloadText.length > 0 ? payloadText : "{}")
        } catch (e) {
            obj = ({})
        }
        // User switching is owned by GuiFacade.  Do not override the current loaded user
        // with a stale controlStateJson.current_user_id captured by an old report card.
        if (obj.user_id !== undefined) delete obj.user_id
        if (actionId === "report.show" || actionId === "report.export" || actionId === "report.export_txt") {
            var sid = safeText(obj.session_id || obj.report_id || "", "")
            if (sid === "n/a" || sid === "no_report_available" || sid.length === 0) {
                sid = reportPrimarySessionId("")
            }
            if (sid.length > 0 && sid !== "n/a" && sid !== "no_report_available") {
                obj.session_id = sid
            } else {
                delete obj.session_id
            }
            obj.allow_latest_fallback = true
        }
        return JSON.stringify(obj)
    }

    function widgetCurrentValue(widgetId) {
        if (widgetId === root.widget1Id) return root.widget1Type === "select" ? root.widget1SelectText : (root.widget1Type === "input" ? root.widget1InputText : widgetDisplayText(root.widget1Type, root.widget1Label, root.widget1Source, root.widget1Fallback, root.widget1Unit, root.widget1Value, root.widget1Id))
        if (widgetId === root.widget2Id) return root.widget2Type === "select" ? root.widget2SelectText : (root.widget2Type === "input" ? root.widget2InputText : widgetDisplayText(root.widget2Type, root.widget2Label, root.widget2Source, root.widget2Fallback, root.widget2Unit, root.widget2Value, root.widget2Id))
        if (widgetId === root.widget3Id) return root.widget3Type === "select" ? root.widget3SelectText : (root.widget3Type === "input" ? root.widget3InputText : widgetDisplayText(root.widget3Type, root.widget3Label, root.widget3Source, root.widget3Fallback, root.widget3Unit, root.widget3Value, root.widget3Id))
        if (widgetId === root.widget4Id) return root.widget4Type === "select" ? root.widget4SelectText : (root.widget4Type === "input" ? root.widget4InputText : widgetDisplayText(root.widget4Type, root.widget4Label, root.widget4Source, root.widget4Fallback, root.widget4Unit, root.widget4Value, root.widget4Id))
        if (widgetId === root.widget5Id) return root.widget5Type === "select" ? root.widget5SelectText : (root.widget5Type === "input" ? root.widget5InputText : widgetDisplayText(root.widget5Type, root.widget5Label, root.widget5Source, root.widget5Fallback, root.widget5Unit, root.widget5Value, root.widget5Id))
        if (widgetId === root.widget6Id) return root.widget6Type === "select" ? root.widget6SelectText : (root.widget6Type === "input" ? root.widget6InputText : widgetDisplayText(root.widget6Type, root.widget6Label, root.widget6Source, root.widget6Fallback, root.widget6Unit, root.widget6Value, root.widget6Id))
        return ""
    }

    function resolveArgsTemplate(argsJson) {
        var text = argsJson && argsJson.length > 0 ? argsJson : "{}"
        var ids = [root.widget1Id, root.widget2Id, root.widget3Id, root.widget4Id, root.widget5Id, root.widget6Id]
        for (var i = 0; i < ids.length; i += 1) {
            var idText = ids[i]
            if (!idText || idText.length === 0) continue
            var value = jsonEscapeText(widgetCurrentValue(idText))
            text = replaceAllText(text, "${input." + idText + "}", value)
            text = replaceAllText(text, "${select." + idText + "}", value)
            text = replaceAllText(text, "${value." + idText + "}", value)
        }
        return text
    }

    function parseArgsObject(argsText) {
        try {
            var obj = JSON.parse(argsText && argsText.length > 0 ? argsText : "{}")
            return obj && typeof obj === "object" ? obj : ({})
        } catch (e) {
            return ({})
        }
    }

    function isAutoDifficultyValue(value) {
        var t = String(value === undefined || value === null ? "" : value).trim().toLowerCase()
        return t.length === 0 || t === "auto" || t === "dynamic" || t === "none" || t === "null" || t === "nan" || t === "n/a"
    }

    function sessionStartPayloadFrom(baseArgsText, currentUser) {
        var payload = parseArgsObject(baseArgsText)
        if (currentUser && currentUser !== "n/a" && (payload.user_id === undefined || payload.user_id === null || payload.user_id === "")) {
            payload.user_id = currentUser
        }
        if (!payload.game_id || payload.game_id === "n/a") {
            payload.game_id = root.widgetCurrentValue("selected_game_id") || sourceValue("gameHudJson.game_id", sourceValue("controlStateJson.current_game_id", "trace_lock"))
        }
        if (!payload.game_id || payload.game_id === "n/a") payload.game_id = "trace_lock"

        var explicitMode = String(payload.difficulty_mode || payload.mode || "").trim().toLowerCase()
        var explicitLevel = payload.difficulty_level !== undefined && payload.difficulty_level !== null ? payload.difficulty_level : (payload.debug_difficulty !== undefined && payload.debug_difficulty !== null ? payload.debug_difficulty : payload.selected_difficulty_level)
        var hudMode = String(sourceValue("gameHudJson.difficulty_mode", "auto")).trim().toLowerCase()
        var hudDebug = sourceValue("gameHudJson.debug_difficulty", "auto")
        var hudHasManual = hudMode === "manual" || !isAutoDifficultyValue(hudDebug)
        var explicitHasManual = explicitMode === "manual" || !isAutoDifficultyValue(explicitLevel)

        // Explicit stale card templates often say auto/auto.  Do not let that
        // erase a difficulty that was already applied in the existing HUD path.
        if (!explicitHasManual && hudHasManual) {
            payload.difficulty_mode = "manual"
            payload.debug_difficulty = hudDebug
            payload.selected_difficulty_level = hudDebug
            payload.difficulty_level = hudDebug
        } else if (explicitHasManual) {
            var level = explicitLevel
            payload.difficulty_mode = "manual"
            payload.debug_difficulty = level
            payload.selected_difficulty_level = level
            payload.difficulty_level = level
        } else {
            payload.difficulty_mode = "auto"
            payload.debug_difficulty = "auto"
            payload.selected_difficulty_level = "auto"
            payload.difficulty_level = null
        }
        return JSON.stringify(payload)
    }

    function actionArgsJson(actionId, argsJson, widgetId) {
        var currentUser = sourceValue("controlStateJson.current_user_id", sourceValue("appState.current_user_id", ""))
        var calibrationId = sourceValue("controlStateJson.last_calibration_id", "")
        var sessionId = sourceValue("sessionState.current_session_id", sourceValue("controlState.current_session_id", ""))
        var hasArgs = argsJson && argsJson.length > 0 && argsJson !== "{}"
        if (hasArgs) {
            var resolved = resolveArgsTemplate(argsJson)
            if (actionId === "session.start") {
                return sessionStartPayloadFrom(resolved, currentUser)
            }
            // Card widgets may define explicit args such as {"calibration_id": "..."}.
            // Preserve those args, but always attach the current GUI user unless the
            // card deliberately provided user_id. This prevents calibration.bind/show
            // from relying on stale facade fallback after switching users.
            if (!isReportAction(actionId) && currentUser && currentUser !== "n/a" && resolved.indexOf("\"user_id\"") < 0) {
                var trimmed = String(resolved).trim()
                if (trimmed === "{}" || trimmed.length === 0) {
                    return "{\"user_id\":\"" + jsonEscapeText(currentUser) + "\"}"
                }
                if (trimmed.charAt(trimmed.length - 1) === "}") {
                    return trimmed.substring(0, trimmed.length - 1) + ",\"user_id\":\"" + jsonEscapeText(currentUser) + "\"}"
                }
            }
            return resolved
        }
        var payload = ({})
        if (!isReportAction(actionId) && currentUser && currentUser !== "n/a") payload.user_id = currentUser
        if ((actionId === "calibration.show" || actionId === "calibration.bind") && calibrationId && calibrationId !== "n/a") payload.calibration_id = calibrationId
        if ((actionId === "report.show" || actionId === "report.show_session" || actionId === "report.export" || actionId === "report.export_txt") && sessionId && sessionId !== "n/a" && sessionId !== "no_report_available") payload.session_id = sessionId
        if (actionId === "session.start") {
            return sessionStartPayloadFrom(JSON.stringify(payload), currentUser)
        }
        return JSON.stringify(payload)
    }

    function extractJsonString(raw, key, fallbackValue) {
        var text = safeText(raw, "")
        if (text.length === 0 || key.length === 0) return safeText(fallbackValue, "")
        var pattern = new RegExp('"' + key + '"\\s*:\\s*"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)"')
        var match = pattern.exec(text)
        if (match && match.length > 1) return match[1].replace(/\\"/g, '"')
        return safeText(fallbackValue, "")
    }

    function extractJsonNumber(raw, key, fallbackValue) {
        var text = safeText(raw, "")
        if (text.length === 0 || key.length === 0) return safeText(fallbackValue, "")
        var pattern = new RegExp('"' + key + '"\\s*:\\s*(-?\\d+(?:\\.\\d+)?)')
        var match = pattern.exec(text)
        if (match && match.length > 1) return match[1]
        return safeText(fallbackValue, "")
    }

    function extractJsonBool(raw, key, fallbackValue) {
        var text = safeText(raw, "")
        if (text.length === 0 || key.length === 0) return safeText(fallbackValue, "")
        var pattern = new RegExp('"' + key + '"\\s*:\\s*(true|false)')
        var match = pattern.exec(text)
        if (match && match.length > 1) return match[1]
        return safeText(fallbackValue, "")
    }

    function profileContextValue(key, fallbackValue) {
        var context = null
        if (root.renderResourcesObj && root.renderResourcesObj.task26_user_profile_context !== undefined) {
            context = root.renderResourcesObj.task26_user_profile_context
        }
        if (context && context[key] !== undefined && context[key] !== null && context[key] !== "") {
            return safeText(context[key], fallbackValue)
        }
        return safeText(fallbackValue, "")
    }

    function meaningfulProfileText(value) {
        var text = safeText(value, "")
        if (text.length === 0) return ""
        var lowered = text.toLowerCase()
        if (lowered === "n/a" || lowered === "none" || lowered === "null" || lowered === "undefined") return ""
        return text
    }

    function profileValue(key, fallbackValue) {
        var raw = root.lastProfileActionRaw.length > 0 ? root.lastProfileActionRaw : root.lastDesktopActionRaw
        var textValue = meaningfulProfileText(extractJsonString(raw, key, ""))
        if (textValue.length > 0) return textValue
        var numberValue = meaningfulProfileText(extractJsonNumber(raw, key, ""))
        if (numberValue.length > 0) return numberValue
        var boolValue = meaningfulProfileText(extractJsonBool(raw, key, ""))
        if (boolValue.length > 0) return boolValue
        var contextValue = meaningfulProfileText(profileContextValue(key, ""))
        if (contextValue.length > 0) return contextValue
        return safeText(fallbackValue, "n/a")
    }

    function calibrationContextValue(key, fallbackValue) {
        var context = null
        if (root.renderResourcesObj && root.renderResourcesObj.task26_calibration_context !== undefined) {
            context = root.renderResourcesObj.task26_calibration_context
        }
        if (context && context[key] !== undefined && context[key] !== null && context[key] !== "") {
            return safeText(context[key], fallbackValue)
        }
        return safeText(fallbackValue, "")
    }

    function calibrationValue(key, fallbackValue) {
        var raw = root.lastCalibrationActionRaw.length > 0 ? root.lastCalibrationActionRaw : root.lastDesktopActionRaw
        var textValue = meaningfulProfileText(extractJsonString(raw, key, ""))
        if (textValue.length > 0) return textValue
        var numberValue = meaningfulProfileText(extractJsonNumber(raw, key, ""))
        if (numberValue.length > 0) return numberValue
        var boolValue = meaningfulProfileText(extractJsonBool(raw, key, ""))
        if (boolValue.length > 0) return boolValue
        var contextValue = meaningfulProfileText(calibrationContextValue(key, ""))
        if (contextValue.length > 0) return contextValue
        return safeText(fallbackValue, "n/a")
    }

    function extractNestedJsonValueFromObject(obj, key, depth) {
        if (!obj || depth <= 0) return ""
        if (obj[key] !== undefined && obj[key] !== null && obj[key] !== "") return safeText(obj[key], "")

        var priority = ["detail", "report", "result", "session", "summary"]
        for (var i = 0; i < priority.length; i++) {
            var name = priority[i]
            if (obj[name] && typeof obj[name] === "object" && !Array.isArray(obj[name])) {
                var direct = extractNestedJsonValueFromObject(obj[name], key, depth - 1)
                if (direct.length > 0) return direct
            }
        }

        for (var prop in obj) {
            if (!obj.hasOwnProperty(prop)) continue
            var value = obj[prop]
            if (value && typeof value === "object" && !Array.isArray(value)) {
                var nested = extractNestedJsonValueFromObject(value, key, depth - 1)
                if (nested.length > 0) return nested
            }
        }
        return ""
    }

    function extractJsonObjectValue(raw, key, fallbackValue) {
        var text = safeText(raw, "")
        if (text.length === 0 || key.length === 0) return safeText(fallbackValue, "")
        try {
            var obj = JSON.parse(text)
            var value = extractNestedJsonValueFromObject(obj, key, 5)
            if (value.length > 0) return value
        } catch (e) {
            return safeText(fallbackValue, "")
        }
        return safeText(fallbackValue, "")
    }

    function currentReportRawObject() {
        var raw = root.lastReportActionRaw.length > 0 ? root.lastReportActionRaw : (root.sharedReportActionRaw.length > 0 ? root.sharedReportActionRaw : root.lastDesktopActionRaw)
        try {
            return JSON.parse(raw || "{}")
        } catch (e) {
            return ({})
        }
    }

    function reportActionIdFromObject(obj) {
        if (!obj || typeof obj !== "object") return ""
        return safeText(obj.action_id || "", "")
    }

    function reportSessionIdFromObject(obj) {
        if (!obj || typeof obj !== "object") return ""
        var result = (obj.result && typeof obj.result === "object") ? obj.result : ({})
        var detail = (obj.detail && typeof obj.detail === "object") ? obj.detail : ({})
        var report = (obj.report && typeof obj.report === "object") ? obj.report : ({})
        var resultDetail = (result.detail && typeof result.detail === "object") ? result.detail : ({})
        var candidates = [
            obj.session_id, result.session_id, detail.session_id, report.session_id, resultDetail.session_id,
            obj.latest_session_id, result.latest_session_id
        ]
        for (var i = 0; i < candidates.length; i += 1) {
            var text = safeText(candidates[i], "").trim()
            if (isValidReportSessionText(text)) return text
        }
        return ""
    }

    function reportExportPathValue(fallbackValue) {
        var obj = currentReportRawObject()
        var actionId = reportActionIdFromObject(obj)
        var selected = safeText(root.sharedSelectedReportSessionId, "").trim()
        var rawSession = reportSessionIdFromObject(obj)
        var raw = root.lastReportActionRaw.length > 0 ? root.lastReportActionRaw : (root.sharedReportActionRaw.length > 0 ? root.sharedReportActionRaw : root.lastDesktopActionRaw)
        var exportPath = meaningfulProfileText(extractJsonObjectValue(raw, "export_path", ""))
        if (exportPath.length === 0) exportPath = meaningfulProfileText(extractJsonString(raw, "export_path", ""))
        if (exportPath.length > 0) {
            if (!isValidReportSessionText(selected) || !isValidReportSessionText(rawSession) || selected === rawSession) {
                return exportPath
            }
        }
        // A report.show/report.latest/report.list result intentionally clears the export path.
        // Export path belongs to a concrete export action; keeping the old global last_export_path
        // after selecting another report made the detail card show a stale TXT path.
        if (actionId === "report.show" || actionId === "report.latest" || actionId === "report.refresh" || actionId === "report.list") {
            return "n/a"
        }
        return safeText(fallbackValue, "n/a")
    }

    function reportListTextFromArray(arr) {
        if (!arr || !Array.isArray(arr) || arr.length === 0) return ""
        var lines = []
        for (var i = 0; i < arr.length; i += 1) {
            var item = arr[i]
            if (!item || typeof item !== "object") continue
            var sid = safeText(item.session_id || item.report_id || item.id || "", "").trim()
            if (!isValidReportSessionText(sid)) continue
            var score = safeText(item.score, "n/a")
            var created = safeText(item.ended_at || item.created_at || item.started_at || "", "n/a")
            var path = safeText(item.report_path || item.latest_report_path || item.source_report_path || "", "n/a")
            // Keep every current-user report in the panel. Do not silently cap to the
            // first ten; the Flickable below handles long lists without inflating the
            // card height.
            lines.push(String(lines.length + 1) + ". " + sid + " | score=" + score + " | time=" + created + "\n   " + path)
        }
        return lines.join("\n")
    }

    function reportListCountFromArray(arr) {
        if (!arr || !Array.isArray(arr) || arr.length === 0) return 0
        var count = 0
        for (var i = 0; i < arr.length; i += 1) {
            var item = arr[i]
            if (!item || typeof item !== "object") continue
            var sid = safeText(item.session_id || item.report_id || item.id || "", "").trim()
            if (isValidReportSessionText(sid)) count += 1
        }
        return count
    }

    function reportListCountFromObject(obj) {
        if (!obj || typeof obj !== "object") return 0
        var count = reportListCountFromArray(obj.items)
        if (count > 0) return count
        count = reportListCountFromArray(obj.sessions)
        if (count > 0) return count
        var result = (obj.result && typeof obj.result === "object") ? obj.result : ({})
        count = reportListCountFromArray(result.items)
        if (count > 0) return count
        count = reportListCountFromArray(result.sessions)
        if (count > 0) return count
        var n = Number(obj.items_count || result.items_count || obj.session_count || result.session_count || 0)
        return isNaN(n) ? 0 : n
    }

    function reportListCountText() {
        var count = reportListCountFromObject(currentReportRawObject())
        if (count <= 0) return ""
        return String(count) + " reports"
    }

    function reportListTextFromObject(obj) {
        if (!obj || typeof obj !== "object") return ""
        var direct = reportListTextFromArray(obj.items)
        if (direct.length > 0) return direct
        direct = reportListTextFromArray(obj.sessions)
        if (direct.length > 0) return direct
        var result = (obj.result && typeof obj.result === "object") ? obj.result : ({})
        direct = reportListTextFromArray(result.items)
        if (direct.length > 0) return direct
        direct = reportListTextFromArray(result.sessions)
        if (direct.length > 0) return direct
        return ""
    }

    function reportListText(fallbackValue) {
        var obj = currentReportRawObject()
        var text = reportListTextFromObject(obj)
        if (text.length > 0) return text
        var contextText = meaningfulProfileText(reportContextValue("report_list_text", ""))
        if (contextText.length > 0) return contextText
        return safeText(fallbackValue, "n/a")
    }

    function reportContextValue(key, fallbackValue) {
        var context = null
        if (root.renderResourcesObj && root.renderResourcesObj.task26_report_context !== undefined) {
            context = root.renderResourcesObj.task26_report_context
        }
        if (context && context[key] !== undefined && context[key] !== null && context[key] !== "") {
            return safeText(context[key], fallbackValue)
        }
        return safeText(fallbackValue, "")
    }

    function reportValue(key, fallbackValue) {
        var raw = root.lastReportActionRaw.length > 0 ? root.lastReportActionRaw : (root.sharedReportActionRaw.length > 0 ? root.sharedReportActionRaw : root.lastDesktopActionRaw)
        var objectValue = meaningfulProfileText(extractJsonObjectValue(raw, key, ""))
        if (objectValue.length > 0) return objectValue
        var textValue = meaningfulProfileText(extractJsonString(raw, key, ""))
        if (textValue.length > 0) return textValue
        var numberValue = meaningfulProfileText(extractJsonNumber(raw, key, ""))
        if (numberValue.length > 0) return numberValue
        var boolValue = meaningfulProfileText(extractJsonBool(raw, key, ""))
        if (boolValue.length > 0) return boolValue
        var contextValue = meaningfulProfileText(reportContextValue(key, ""))
        if (contextValue.length > 0) return contextValue
        return safeText(fallbackValue, "n/a")
    }

    function summarizeActionResult(raw, actionId) {
        var status = extractJsonString(raw, "status", "accepted")
        var message = extractJsonString(raw, "message", "")
        var result = extractJsonString(raw, "result", "")
        var itemsCount = extractJsonNumber(raw, "items_count", "")
        var userCount = extractJsonNumber(raw, "user_count", "")
        var calibrationCount = extractJsonNumber(raw, "calibration_count", "")
        var sessionId = extractJsonString(raw, "session_id", "")
        var reportPath = extractJsonString(raw, "report_path", "")

        var detail = message.length > 0 ? message : result
        if (itemsCount.length > 0) detail = itemsCount + " items"
        else if (userCount.length > 0) detail = userCount + " users"
        else if (calibrationCount.length > 0) detail = calibrationCount + " calibrations"
        else if (sessionId.length > 0) detail = sessionId
        else if (reportPath.length > 0) detail = reportPath
        if (detail.length === 0) detail = raw && raw.length > 0 ? "returned" : "no result text"
        if (detail.length > 96) detail = detail.slice(0, 93) + "..."
        return status + " · " + detail
    }

    // Compatibility token for legacy static tests: invokeDesktopAction(actionId)
    function invokeDesktopAction(actionId, argsJson, widgetId) {
        if (!actionId || actionId.length === 0) {
            root.lastDesktopActionId = ""
            root.lastDesktopActionStatus = "missing_action"
            root.lastDesktopActionMessage = "empty action_id"
            return ""
        }
        var payloadText = sanitizeReportPayloadText(actionId, actionArgsJson(actionId, argsJson, widgetId), widgetId)
        if ((actionId === "report.show" || actionId === "report.export" || actionId === "report.export_txt") && payloadText.indexOf("no_report_available") >= 0) {
            payloadText = payloadText.replace(/"session_id"\s*:\s*"no_report_available"\s*,?/, "")
            payloadText = payloadText.replace(/,\s*}/g, "}").replace(/{\s*,/g, "{")
        }
        root.lastDesktopActionId = actionId
        root.lastDesktopActionStatus = "clicked"
        root.lastDesktopActionMessage = widgetId && widgetId.length > 0 ? widgetId : "desktop card button"
        console.log("[DESKTOP CARD CLICK] card_id=" + root.cardId + " widget_id=" + safeText(widgetId, "n/a") + " action_id=" + actionId + " args=" + payloadText)
        if (!root.guiBridge) {
            root.lastDesktopActionStatus = "missing_bridge"
            root.lastDesktopActionMessage = "guiBridge is null"
            console.log("[DESKTOP CARD ACTION] action_id=" + actionId + " status=missing_bridge")
            return ""
        }
        try {
            var raw = root.guiBridge.invokeAction(actionId, payloadText)
            root.lastDesktopActionRaw = safeText(raw, "")
            if (actionId === "user.show_profile" || actionId === "user.load") {
                root.lastProfileActionRaw = root.lastDesktopActionRaw
            }
            if (actionId.indexOf("calibration.") === 0) {
                root.lastCalibrationActionRaw = root.lastDesktopActionRaw
            }
            if (actionId.indexOf("report.") === 0) {
                root.lastReportActionRaw = root.lastDesktopActionRaw
                root.reportActionResultReady(root.lastReportActionRaw)
            }
            var statusText = extractJsonString(raw, "status", raw && raw.length > 0 ? "returned" : "accepted")
            root.lastDesktopActionStatus = statusText
            root.lastDesktopActionMessage = summarizeActionResult(raw, actionId)
            console.log("[DESKTOP CARD ACTION] action_id=" + actionId + " status=" + statusText + " summary=" + root.lastDesktopActionMessage + " raw_len=" + String(raw ? raw.length : 0))
            if (actionId === "user.show_profile" || (widgetId && widgetId.indexOf("profile_popup") >= 0)) {
                profilePopup.open()
            }
            if (actionId === "calibration.show"
                    || actionId === "calibration.latest"
                    || (widgetId && widgetId.indexOf("show_selected_calibration") >= 0)
                    || (widgetId && widgetId.indexOf("show_manual_calibration") >= 0)
                    || (widgetId && widgetId.indexOf("latest_calibration") >= 0)) {
                calibrationPopup.open()
            }
            if (actionId === "report.show"
                    || actionId === "report.latest"
                    || actionId === "report.export"
                    || actionId === "report.export_txt"
                    || (widgetId && widgetId.indexOf("show_selected_report") >= 0)
                    || (widgetId && widgetId.indexOf("latest_report") >= 0)
                    || (widgetId && widgetId.indexOf("export_report") >= 0)) {
                reportPopup.open()
            }
            return raw
        } catch (e) {
            root.lastDesktopActionStatus = "error"
            root.lastDesktopActionMessage = String(e)
            console.log("[DESKTOP CARD ACTION] action_id=" + actionId + " status=error message=" + String(e))
            return ""
        }
    }

    DesignCard {
        anchors.fill: parent
        cardTitle: root.cardTitleText.length > 0 ? root.cardTitleText : root.cardId
        cardSubtitle: root.cardSubtitleText.length > 0 ? root.cardSubtitleText : root.cardType
        backgroundColor: root.cardBackgroundColor.length > 0 ? root.cardBackgroundColor : (root.placeholder ? "#2A2337" : "#151B24")
        backgroundOpacity: root.cardBackgroundOpacity
        backgroundImage: root.cardBackgroundImage
        borderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : (root.requiredCard ? "#5D8CFF" : "#2B3A4C")
        borderWidth: root.lockedCard ? Math.max(2, root.cardBorderWidth) : root.cardBorderWidth
        radiusValue: root.cardRadiusValue
        shapeType: root.cardShapeType
        paddingValue: 8
        titlePixelSize: root.titlePixelSize
        subtitlePixelSize: root.subtitlePixelSize
        headerSpacing: root.headerSpacing
        contentSpacing: root.contentSpacing
        glassEnabled: root.cardGlassEnabled
        glassTintColor: root.cardGlassTintColor
        glassOpacity: root.cardGlassOpacity
        glassHighlight: root.cardGlassHighlight

        Loader {
            id: desktopGameCanvasLoader
            anchors.fill: parent
            active: root.visible && root.isGameCanvasCard()
            visible: active
            asynchronous: false
            sourceComponent: Component {
                GameCanvas {
                    id: desktopGameCanvas
                    anchors.fill: parent
                    gameView: root.gameViewObj
                    guiBridgeRef: root.guiBridge
                    fallbackGameId: root.sourceValue("gameHudJson.game_id", root.sourceValue("controlStateJson.current_game_id", "trace_lock"))
                    designThemeObj: root.designThemeObj
                    gameStyleObj: root.gameStyleObj
                    effectStyleObj: root.effectStyleObj
                    renderResourcesObj: root.renderResourcesObj
                    diagnosticEnabled: false
                }
            }
        }

        Rectangle {
            id: gameCanvasHudOverlay
            visible: desktopGameCanvasLoader.active
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: 10
            width: Math.min(parent.width - 20, 380)
            height: Math.min(parent.height - 20, 132)
            radius: 16
            color: "#06111D"
            opacity: 0.68
            border.color: "#4FE3D2"
            border.width: 1
            z: 20

            Column {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 4

                Text {
                    width: parent.width
                    text: "HEAD UP DISPLAY · " + root.sourceValue("gameHudJson.game_id", "trace_lock")
                    color: "#DDFBFF"
                    font.pixelSize: Math.max(10, root.widgetMetaPixelSize)
                    font.bold: true
                    elide: Text.ElideRight
                }

                Row {
                    width: parent.width
                    spacing: 10

                    Text { width: Math.floor((parent.width - 20) / 3); text: "Score " + root.sourceValue("gameHudJson.score", "0"); color: "#EAF2FF"; font.pixelSize: Math.max(11, root.widgetValuePixelSize); font.bold: true; elide: Text.ElideRight }
                    Text { width: Math.floor((parent.width - 20) / 3); text: "Combo " + root.sourceValue("gameHudJson.combo", "0"); color: "#EAF2FF"; font.pixelSize: Math.max(11, root.widgetValuePixelSize); font.bold: true; elide: Text.ElideRight }
                    Text { width: Math.floor((parent.width - 20) / 3); text: "Lv " + root.sourceValue("gameHudJson.effective_level", root.sourceValue("gameHudJson.level", "n/a")); color: "#EAF2FF"; font.pixelSize: Math.max(11, root.widgetValuePixelSize); font.bold: true; elide: Text.ElideRight }
                }

                Row {
                    width: parent.width
                    spacing: 10

                    Text { width: Math.floor((parent.width - 20) / 3); text: "Time " + root.sourceValue("gameHudJson.time_left_ms", "n/a"); color: "#9BE7C0"; font.pixelSize: Math.max(9, root.widgetLabelPixelSize); elide: Text.ElideRight }
                    Text { width: Math.floor((parent.width - 20) / 3); text: "FI " + root.sourceValue("runtimeSnapshot.fi", root.sourceValue("runtimeSnapshot.fi_smoothed", "n/a")); color: "#9BE7C0"; font.pixelSize: Math.max(9, root.widgetLabelPixelSize); elide: Text.ElideRight }
                    Text { width: Math.floor((parent.width - 20) / 3); text: "SQI " + root.sourceValue("runtimeSnapshot.sqi", "n/a"); color: "#9BE7C0"; font.pixelSize: Math.max(9, root.widgetLabelPixelSize); elide: Text.ElideRight }
                }

                Row {
                    width: parent.width
                    spacing: 10

                    Text { width: Math.floor((parent.width - 20) / 3); text: "Diff " + root.sourceValue("gameHudJson.difficulty_mode", "auto") + "/" + root.sourceValue("gameHudJson.debug_difficulty", "auto"); color: "#BFDFFF"; font.pixelSize: Math.max(9, root.widgetLabelPixelSize); elide: Text.ElideRight }
                    Text { width: Math.floor((parent.width - 20) / 3); text: "DDA " + root.sourceValue("gameHudJson.dynamic_difficulty_enabled", "n/a"); color: "#BFDFFF"; font.pixelSize: Math.max(9, root.widgetLabelPixelSize); elide: Text.ElideRight }
                    Text { width: Math.floor((parent.width - 20) / 3); text: "Attn " + root.sourceValue("runtimeSnapshot.attention", "n/a"); color: "#BFDFFF"; font.pixelSize: Math.max(9, root.widgetLabelPixelSize); elide: Text.ElideRight }
                }
            }
        }

        Column {
            id: bodyColumn
            visible: !root.isGameCanvasCard()
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            spacing: root.widgetSpacing
            clip: true

            Item {
                width: parent.width
                height: 14
                clip: true
                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width * 0.55
                    text: root.cardType.length > 0 ? root.cardType : "card"
                    color: "#8EA4BF"
                    font.pixelSize: root.feedbackPixelSize
                    maximumLineCount: 2
                    wrapMode: Text.Wrap
                    elide: Text.ElideRight
                }
                Text {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width * 0.42
                    text: (root.lockedCard ? "locked" : "free") + " · " + String(root.widgetCount)
                    color: root.lockedCard ? "#FFD479" : "#8EA4BF"
                    font.pixelSize: root.widgetMetaPixelSize
                    horizontalAlignment: Text.AlignRight
                    elide: Text.ElideRight
                }
            }

            Item { width: parent.width; height: root.bodyTopMargin }

            Item {
                id: inlineActionFeedback
                width: parent.width
                height: root.lastDesktopActionId.length > 0 ? Math.max(16, root.feedbackPixelSize + 8) : 0
                visible: root.lastDesktopActionId.length > 0
                enabled: false
                clip: true

                Rectangle {
                    anchors.fill: parent
                    radius: Math.max(6, root.cardRadiusValue / 4)
                    color: root.lastDesktopActionStatus === "error" || root.lastDesktopActionStatus === "missing_bridge" ? "#31161A" : "#0E1C18"
                    opacity: 0.66
                    border.color: root.lastDesktopActionStatus === "error" || root.lastDesktopActionStatus === "missing_bridge" ? "#FF7A7A" : "#2F6B4D"
                    border.width: 1
                }

                Text {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 8
                    text: "last: " + root.lastDesktopActionId + " · " + root.lastDesktopActionMessage
                    color: root.lastDesktopActionStatus === "error" || root.lastDesktopActionStatus === "missing_bridge" ? "#FF9A9A" : "#9BE7C0"
                    font.pixelSize: root.feedbackPixelSize
                    maximumLineCount: 1
                    wrapMode: Text.NoWrap
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                }
            }

            Item {
                width: parent.width
                height: widgetVisible(root.widget1Type, 1) ? rowHeightFor(root.widget1Type) : 0
                visible: widgetVisible(root.widget1Type, 1)
                clip: true

                ConfigButtonWidget {
                    width: parent.width
                    buttonWidth: parent.width
                    buttonHeight: root.buttonHeight
                    textPixelSize: root.widgetValuePixelSize
                    visible: root.widget1Type === "button"
                    guiBridge: null
                    label: buttonLabel(root.widget1Label, root.widget1ActionId, root.widget1Required)
                    actionId: root.widget1ActionId
                    argsJson: root.widget1ArgsJson
                    variant: root.widget1Variant
                    required: root.widget1Required
                    onActionRequested: function(actionId) { root.invokeDesktopAction(actionId, root.widget1ArgsJson, root.widget1Id) }
                }

                TextField {
                    visible: root.widget1Type === "input"
                    width: parent.width
                    height: root.buttonHeight
                    placeholderText: root.widget1Fallback.length > 0 ? root.widget1Fallback : root.widget1Label
                    text: root.widget1InputText
                    Component.onCompleted: {
                        if (root.widget1InputText.length === 0) {
                            root.widget1InputText = root.widget1Value.length > 0 ? root.widget1Value : root.widget1Fallback
                        }
                    }
                    color: "#EAF2FF"
                    placeholderTextColor: "#7F8DA3"
                    font.pixelSize: root.widgetValuePixelSize
                    selectByMouse: true
                    onTextChanged: root.widget1InputText = text
                    background: Rectangle {
                        radius: Math.max(6, root.cardRadiusValue / 2)
                        color: "#182130"
                        border.color: "#465A78"
                        border.width: 1
                    }
                }

                ConfigSelectWidget {
                    visible: root.widget1Type === "select"
                    width: parent.width
                    height: root.buttonHeight
                    optionsText: root.widget1Id === "report_selector" ? root.reportSelectorOptionsText(root.widget1OptionsText) : root.widget1OptionsText
                    fallbackText: root.widget1Fallback
                    textPixelSize: root.widgetValuePixelSize
                    itemHeight: Math.max(24, root.buttonHeight)
                    cornerRadius: Math.max(8, root.cardRadiusValue / 2)
                    popupCornerRadius: Math.max(10, root.cardRadiusValue / 2)
                    backgroundColor: "#182130"
                    borderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    popupBackgroundColor: "#121926"
                    popupBorderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    onCurrentTextChanged: {
                        root.widget1SelectText = currentText
                        if (root.widget1Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                    Component.onCompleted: {
                        root.widget1SelectText = currentText
                        if (root.widget1Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                }

                Text { visible: root.widget1Type !== "button" && root.widget1Type !== "input" && root.widget1Type !== "select" && root.widget1Type !== "text"; width: parent.width * 0.40; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; text: root.widget1Label.length > 0 ? root.widget1Label : root.widget1Id; color: "#8EA4BF"; font.pixelSize: root.widgetLabelPixelSize; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget1Type !== "button" && root.widget1Type !== "input" && root.widget1Type !== "select" && root.widget1Type !== "text"; width: parent.width * 0.58; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: root.widgetDisplayText(root.widget1Type, root.widget1Label, root.widget1Source, root.widget1Fallback, root.widget1Unit, root.widget1Value, root.widget1Id); color: "#EAF2FF"; font.pixelSize: root.widgetValuePixelSize; font.bold: root.widget1Type === "metric"; horizontalAlignment: Text.AlignRight; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget1Type === "text"; width: parent.width; anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: (root.widget1Label.length > 0 ? root.widget1Label + ": " : "") + root.widgetDisplayText(root.widget1Type, root.widget1Label, root.widget1Source, root.widget1Fallback, root.widget1Unit, root.widget1Value, root.widget1Id); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; maximumLineCount: 4; wrapMode: Text.Wrap; elide: Text.ElideRight }
            }

            Item {
                width: parent.width
                height: widgetVisible(root.widget2Type, 2) ? rowHeightFor(root.widget2Type) : 0
                visible: widgetVisible(root.widget2Type, 2)
                clip: true

                ConfigButtonWidget {
                    width: parent.width
                    buttonWidth: parent.width
                    buttonHeight: root.buttonHeight
                    textPixelSize: root.widgetValuePixelSize
                    visible: root.widget2Type === "button"
                    guiBridge: null
                    label: buttonLabel(root.widget2Label, root.widget2ActionId, root.widget2Required)
                    actionId: root.widget2ActionId
                    argsJson: root.widget2ArgsJson
                    variant: root.widget2Variant
                    required: root.widget2Required
                    onActionRequested: function(actionId) { root.invokeDesktopAction(actionId, root.widget2ArgsJson, root.widget2Id) }
                }

                TextField {
                    visible: root.widget2Type === "input"
                    width: parent.width
                    height: root.buttonHeight
                    placeholderText: root.widget2Fallback.length > 0 ? root.widget2Fallback : root.widget2Label
                    text: root.widget2InputText
                    Component.onCompleted: {
                        if (root.widget2InputText.length === 0) {
                            root.widget2InputText = root.widget2Value.length > 0 ? root.widget2Value : root.widget2Fallback
                        }
                    }
                    color: "#EAF2FF"
                    placeholderTextColor: "#7F8DA3"
                    font.pixelSize: root.widgetValuePixelSize
                    selectByMouse: true
                    onTextChanged: root.widget2InputText = text
                    background: Rectangle {
                        radius: Math.max(6, root.cardRadiusValue / 2)
                        color: "#182130"
                        border.color: "#465A78"
                        border.width: 1
                    }
                }

                ConfigSelectWidget {
                    visible: root.widget2Type === "select"
                    width: parent.width
                    height: root.buttonHeight
                    optionsText: root.widget2Id === "report_selector" ? root.reportSelectorOptionsText(root.widget2OptionsText) : root.widget2OptionsText
                    fallbackText: root.widget2Fallback
                    textPixelSize: root.widgetValuePixelSize
                    itemHeight: Math.max(24, root.buttonHeight)
                    cornerRadius: Math.max(8, root.cardRadiusValue / 2)
                    popupCornerRadius: Math.max(10, root.cardRadiusValue / 2)
                    backgroundColor: "#182130"
                    borderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    popupBackgroundColor: "#121926"
                    popupBorderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    onCurrentTextChanged: {
                        root.widget2SelectText = currentText
                        if (root.widget2Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                    Component.onCompleted: {
                        root.widget2SelectText = currentText
                        if (root.widget2Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                }

                Text { visible: root.widget2Type !== "button" && root.widget2Type !== "input" && root.widget2Type !== "select" && root.widget2Type !== "text"; width: parent.width * 0.40; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; text: root.widget2Label.length > 0 ? root.widget2Label : root.widget2Id; color: "#8EA4BF"; font.pixelSize: root.widgetLabelPixelSize; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget2Type !== "button" && root.widget2Type !== "input" && root.widget2Type !== "select" && root.widget2Type !== "text"; width: parent.width * 0.58; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: root.widgetDisplayText(root.widget2Type, root.widget2Label, root.widget2Source, root.widget2Fallback, root.widget2Unit, root.widget2Value, root.widget2Id); color: "#EAF2FF"; font.pixelSize: root.widgetValuePixelSize; font.bold: root.widget2Type === "metric"; horizontalAlignment: Text.AlignRight; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget2Type === "text"; width: parent.width; anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: (root.widget2Label.length > 0 ? root.widget2Label + ": " : "") + root.widgetDisplayText(root.widget2Type, root.widget2Label, root.widget2Source, root.widget2Fallback, root.widget2Unit, root.widget2Value, root.widget2Id); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; maximumLineCount: 4; wrapMode: Text.Wrap; elide: Text.ElideRight }
            }

            Item {
                width: parent.width
                height: widgetVisible(root.widget3Type, 3) ? rowHeightFor(root.widget3Type) : 0
                visible: widgetVisible(root.widget3Type, 3)
                clip: true

                ConfigButtonWidget {
                    width: parent.width
                    buttonWidth: parent.width
                    buttonHeight: root.buttonHeight
                    textPixelSize: root.widgetValuePixelSize
                    visible: root.widget3Type === "button"
                    guiBridge: null
                    label: buttonLabel(root.widget3Label, root.widget3ActionId, root.widget3Required)
                    actionId: root.widget3ActionId
                    argsJson: root.widget3ArgsJson
                    variant: root.widget3Variant
                    required: root.widget3Required
                    onActionRequested: function(actionId) { root.invokeDesktopAction(actionId, root.widget3ArgsJson, root.widget3Id) }
                }

                TextField {
                    visible: root.widget3Type === "input"
                    width: parent.width
                    height: root.buttonHeight
                    placeholderText: root.widget3Fallback.length > 0 ? root.widget3Fallback : root.widget3Label
                    text: root.widget3InputText
                    Component.onCompleted: {
                        if (root.widget3InputText.length === 0) {
                            root.widget3InputText = root.widget3Value.length > 0 ? root.widget3Value : root.widget3Fallback
                        }
                    }
                    color: "#EAF2FF"
                    placeholderTextColor: "#7F8DA3"
                    font.pixelSize: root.widgetValuePixelSize
                    selectByMouse: true
                    onTextChanged: root.widget3InputText = text
                    background: Rectangle {
                        radius: Math.max(6, root.cardRadiusValue / 2)
                        color: "#182130"
                        border.color: "#465A78"
                        border.width: 1
                    }
                }

                ConfigSelectWidget {
                    visible: root.widget3Type === "select"
                    width: parent.width
                    height: root.buttonHeight
                    optionsText: root.widget3Id === "report_selector" ? root.reportSelectorOptionsText(root.widget3OptionsText) : root.widget3OptionsText
                    fallbackText: root.widget3Fallback
                    textPixelSize: root.widgetValuePixelSize
                    itemHeight: Math.max(24, root.buttonHeight)
                    cornerRadius: Math.max(8, root.cardRadiusValue / 2)
                    popupCornerRadius: Math.max(10, root.cardRadiusValue / 2)
                    backgroundColor: "#182130"
                    borderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    popupBackgroundColor: "#121926"
                    popupBorderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    onCurrentTextChanged: {
                        root.widget3SelectText = currentText
                        if (root.widget3Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                    Component.onCompleted: {
                        root.widget3SelectText = currentText
                        if (root.widget3Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                }

                Text { visible: root.widget3Type !== "button" && root.widget3Type !== "input" && root.widget3Type !== "select" && root.widget3Type !== "text"; width: parent.width * 0.40; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; text: root.widget3Label.length > 0 ? root.widget3Label : root.widget3Id; color: "#8EA4BF"; font.pixelSize: root.widgetLabelPixelSize; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget3Type !== "button" && root.widget3Type !== "input" && root.widget3Type !== "select" && root.widget3Type !== "text"; width: parent.width * 0.58; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: root.widgetDisplayText(root.widget3Type, root.widget3Label, root.widget3Source, root.widget3Fallback, root.widget3Unit, root.widget3Value, root.widget3Id); color: "#EAF2FF"; font.pixelSize: root.widgetValuePixelSize; font.bold: root.widget3Type === "metric"; horizontalAlignment: Text.AlignRight; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget3Type === "text"; width: parent.width; anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: (root.widget3Label.length > 0 ? root.widget3Label + ": " : "") + root.widgetDisplayText(root.widget3Type, root.widget3Label, root.widget3Source, root.widget3Fallback, root.widget3Unit, root.widget3Value, root.widget3Id); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; maximumLineCount: 4; wrapMode: Text.Wrap; elide: Text.ElideRight }
            }

            Item {
                width: parent.width
                height: widgetVisible(root.widget4Type, 4) ? rowHeightFor(root.widget4Type) : 0
                visible: widgetVisible(root.widget4Type, 4)
                clip: true

                ConfigButtonWidget {
                    width: parent.width
                    buttonWidth: parent.width
                    buttonHeight: root.buttonHeight
                    textPixelSize: root.widgetValuePixelSize
                    visible: root.widget4Type === "button"
                    guiBridge: null
                    label: buttonLabel(root.widget4Label, root.widget4ActionId, root.widget4Required)
                    actionId: root.widget4ActionId
                    argsJson: root.widget4ArgsJson
                    variant: root.widget4Variant
                    required: root.widget4Required
                    onActionRequested: function(actionId) { root.invokeDesktopAction(actionId, root.widget4ArgsJson, root.widget4Id) }
                }

                TextField {
                    visible: root.widget4Type === "input"
                    width: parent.width
                    height: root.buttonHeight
                    placeholderText: root.widget4Fallback.length > 0 ? root.widget4Fallback : root.widget4Label
                    text: root.widget4InputText
                    Component.onCompleted: {
                        if (root.widget4InputText.length === 0) {
                            root.widget4InputText = root.widget4Value.length > 0 ? root.widget4Value : root.widget4Fallback
                        }
                    }
                    color: "#EAF2FF"
                    placeholderTextColor: "#7F8DA3"
                    font.pixelSize: root.widgetValuePixelSize
                    selectByMouse: true
                    onTextChanged: root.widget4InputText = text
                    background: Rectangle {
                        radius: Math.max(6, root.cardRadiusValue / 2)
                        color: "#182130"
                        border.color: "#465A78"
                        border.width: 1
                    }
                }

                ConfigSelectWidget {
                    visible: root.widget4Type === "select"
                    width: parent.width
                    height: root.buttonHeight
                    optionsText: root.widget4Id === "report_selector" ? root.reportSelectorOptionsText(root.widget4OptionsText) : root.widget4OptionsText
                    fallbackText: root.widget4Fallback
                    textPixelSize: root.widgetValuePixelSize
                    itemHeight: Math.max(24, root.buttonHeight)
                    cornerRadius: Math.max(8, root.cardRadiusValue / 2)
                    popupCornerRadius: Math.max(10, root.cardRadiusValue / 2)
                    backgroundColor: "#182130"
                    borderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    popupBackgroundColor: "#121926"
                    popupBorderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    onCurrentTextChanged: {
                        root.widget4SelectText = currentText
                        if (root.widget4Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                    Component.onCompleted: {
                        root.widget4SelectText = currentText
                        if (root.widget4Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                }

                Text { visible: root.widget4Type !== "button" && root.widget4Type !== "input" && root.widget4Type !== "select" && root.widget4Type !== "text"; width: parent.width * 0.40; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; text: root.widget4Label.length > 0 ? root.widget4Label : root.widget4Id; color: "#8EA4BF"; font.pixelSize: root.widgetLabelPixelSize; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget4Type !== "button" && root.widget4Type !== "input" && root.widget4Type !== "select" && root.widget4Type !== "text"; width: parent.width * 0.58; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: root.widgetDisplayText(root.widget4Type, root.widget4Label, root.widget4Source, root.widget4Fallback, root.widget4Unit, root.widget4Value, root.widget4Id); color: "#EAF2FF"; font.pixelSize: root.widgetValuePixelSize; font.bold: root.widget4Type === "metric"; horizontalAlignment: Text.AlignRight; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget4Type === "text"; width: parent.width; anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: (root.widget4Label.length > 0 ? root.widget4Label + ": " : "") + root.widgetDisplayText(root.widget4Type, root.widget4Label, root.widget4Source, root.widget4Fallback, root.widget4Unit, root.widget4Value, root.widget4Id); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; maximumLineCount: 4; wrapMode: Text.Wrap; elide: Text.ElideRight }
            }

            Item {
                width: parent.width
                height: widgetVisible(root.widget5Type, 5) ? rowHeightFor(root.widget5Type) : 0
                visible: widgetVisible(root.widget5Type, 5)
                clip: true

                ConfigButtonWidget {
                    width: parent.width
                    buttonWidth: parent.width
                    buttonHeight: root.buttonHeight
                    textPixelSize: root.widgetValuePixelSize
                    visible: root.widget5Type === "button"
                    guiBridge: null
                    label: buttonLabel(root.widget5Label, root.widget5ActionId, root.widget5Required)
                    actionId: root.widget5ActionId
                    argsJson: root.widget5ArgsJson
                    variant: root.widget5Variant
                    required: root.widget5Required
                    onActionRequested: function(actionId) { root.invokeDesktopAction(actionId, root.widget5ArgsJson, root.widget5Id) }
                }

                TextField {
                    visible: root.widget5Type === "input"
                    width: parent.width
                    height: root.buttonHeight
                    placeholderText: root.widget5Fallback.length > 0 ? root.widget5Fallback : root.widget5Label
                    text: root.widget5InputText
                    Component.onCompleted: {
                        if (root.widget5InputText.length === 0) {
                            root.widget5InputText = root.widget5Value.length > 0 ? root.widget5Value : root.widget5Fallback
                        }
                    }
                    color: "#EAF2FF"
                    placeholderTextColor: "#7F8DA3"
                    font.pixelSize: root.widgetValuePixelSize
                    selectByMouse: true
                    onTextChanged: root.widget5InputText = text
                    background: Rectangle {
                        radius: Math.max(6, root.cardRadiusValue / 2)
                        color: "#182130"
                        border.color: "#465A78"
                        border.width: 1
                    }
                }

                ConfigSelectWidget {
                    visible: root.widget5Type === "select"
                    width: parent.width
                    height: root.buttonHeight
                    optionsText: root.widget5Id === "report_selector" ? root.reportSelectorOptionsText(root.widget5OptionsText) : root.widget5OptionsText
                    fallbackText: root.widget5Fallback
                    textPixelSize: root.widgetValuePixelSize
                    itemHeight: Math.max(24, root.buttonHeight)
                    cornerRadius: Math.max(8, root.cardRadiusValue / 2)
                    popupCornerRadius: Math.max(10, root.cardRadiusValue / 2)
                    backgroundColor: "#182130"
                    borderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    popupBackgroundColor: "#121926"
                    popupBorderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    onCurrentTextChanged: {
                        root.widget5SelectText = currentText
                        if (root.widget5Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                    Component.onCompleted: {
                        root.widget5SelectText = currentText
                        if (root.widget5Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                }

                Text { visible: root.widget5Type !== "button" && root.widget5Type !== "input" && root.widget5Type !== "select" && root.widget5Type !== "text"; width: parent.width * 0.40; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; text: root.widget5Label.length > 0 ? root.widget5Label : root.widget5Id; color: "#8EA4BF"; font.pixelSize: root.widgetLabelPixelSize; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget5Type !== "button" && root.widget5Type !== "input" && root.widget5Type !== "select" && root.widget5Type !== "text"; width: parent.width * 0.58; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: root.widgetDisplayText(root.widget5Type, root.widget5Label, root.widget5Source, root.widget5Fallback, root.widget5Unit, root.widget5Value, root.widget5Id); color: "#EAF2FF"; font.pixelSize: root.widgetValuePixelSize; font.bold: root.widget5Type === "metric"; horizontalAlignment: Text.AlignRight; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget5Type === "text"; width: parent.width; anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: (root.widget5Label.length > 0 ? root.widget5Label + ": " : "") + root.widgetDisplayText(root.widget5Type, root.widget5Label, root.widget5Source, root.widget5Fallback, root.widget5Unit, root.widget5Value, root.widget5Id); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; maximumLineCount: 4; wrapMode: Text.Wrap; elide: Text.ElideRight }
            }

            Item {
                width: parent.width
                height: widgetVisible(root.widget6Type, 6) ? rowHeightFor(root.widget6Type) : 0
                visible: widgetVisible(root.widget6Type, 6)
                clip: true

                ConfigButtonWidget {
                    width: parent.width
                    buttonWidth: parent.width
                    buttonHeight: root.buttonHeight
                    textPixelSize: root.widgetValuePixelSize
                    visible: root.widget6Type === "button"
                    guiBridge: null
                    label: buttonLabel(root.widget6Label, root.widget6ActionId, root.widget6Required)
                    actionId: root.widget6ActionId
                    argsJson: root.widget6ArgsJson
                    variant: root.widget6Variant
                    required: root.widget6Required
                    onActionRequested: function(actionId) { root.invokeDesktopAction(actionId, root.widget6ArgsJson, root.widget6Id) }
                }

                TextField {
                    visible: root.widget6Type === "input"
                    width: parent.width
                    height: root.buttonHeight
                    placeholderText: root.widget6Fallback.length > 0 ? root.widget6Fallback : root.widget6Label
                    text: root.widget6InputText
                    Component.onCompleted: {
                        if (root.widget6InputText.length === 0) {
                            root.widget6InputText = root.widget6Value.length > 0 ? root.widget6Value : root.widget6Fallback
                        }
                    }
                    color: "#EAF2FF"
                    placeholderTextColor: "#7F8DA3"
                    font.pixelSize: root.widgetValuePixelSize
                    selectByMouse: true
                    onTextChanged: root.widget6InputText = text
                    background: Rectangle {
                        radius: Math.max(6, root.cardRadiusValue / 2)
                        color: "#182130"
                        border.color: "#465A78"
                        border.width: 1
                    }
                }

                ConfigSelectWidget {
                    visible: root.widget6Type === "select"
                    width: parent.width
                    height: root.buttonHeight
                    optionsText: root.widget6Id === "report_selector" ? root.reportSelectorOptionsText(root.widget6OptionsText) : root.widget6OptionsText
                    fallbackText: root.widget6Fallback
                    textPixelSize: root.widgetValuePixelSize
                    itemHeight: Math.max(24, root.buttonHeight)
                    cornerRadius: Math.max(8, root.cardRadiusValue / 2)
                    popupCornerRadius: Math.max(10, root.cardRadiusValue / 2)
                    backgroundColor: "#182130"
                    borderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    popupBackgroundColor: "#121926"
                    popupBorderColor: root.cardBorderColor.length > 0 ? root.cardBorderColor : "#465A78"
                    onCurrentTextChanged: {
                        root.widget6SelectText = currentText
                        if (root.widget6Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                    Component.onCompleted: {
                        root.widget6SelectText = currentText
                        if (root.widget6Id === "report_selector") root.rememberReportSelection(currentText)
                    }
                }

                Text { visible: root.widget6Type !== "button" && root.widget6Type !== "input" && root.widget6Type !== "select" && root.widget6Type !== "text"; width: parent.width * 0.40; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; text: root.widget6Label.length > 0 ? root.widget6Label : root.widget6Id; color: "#8EA4BF"; font.pixelSize: root.widgetLabelPixelSize; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget6Type !== "button" && root.widget6Type !== "input" && root.widget6Type !== "select" && root.widget6Type !== "text"; width: parent.width * 0.58; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: root.widgetDisplayText(root.widget6Type, root.widget6Label, root.widget6Source, root.widget6Fallback, root.widget6Unit, root.widget6Value, root.widget6Id); color: "#EAF2FF"; font.pixelSize: root.widgetValuePixelSize; font.bold: root.widget6Type === "metric"; horizontalAlignment: Text.AlignRight; maximumLineCount: 1; wrapMode: Text.NoWrap; elide: Text.ElideRight }
                Text { visible: root.widget6Type === "text"; width: parent.width; anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: (root.widget6Label.length > 0 ? root.widget6Label + ": " : "") + root.widgetDisplayText(root.widget6Type, root.widget6Label, root.widget6Source, root.widget6Fallback, root.widget6Unit, root.widget6Value, root.widget6Id); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; maximumLineCount: 4; wrapMode: Text.Wrap; elide: Text.ElideRight }
            }

            Rectangle {
                id: reportListPanel
                width: parent.width
                height: root.reportListPanelVisible() ? Math.max(220, Math.min(360, parent.height * 0.44)) : 0
                visible: root.reportListPanelVisible()
                radius: 16
                color: "#09111F"
                border.color: "#34506F"
                border.width: 1
                clip: true

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 1
                    radius: 15
                    color: "transparent"
                    border.color: "#11243A"
                    border.width: 1
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 7

                    Row {
                        width: parent.width
                        height: 22
                        spacing: 8

                        Text {
                            width: Math.max(1, parent.width - reportListCountBadge.width - 10)
                            height: parent.height
                            text: "Current User Reports"
                            color: "#EAF2FF"
                            font.pixelSize: Math.max(12, root.widgetValuePixelSize)
                            font.bold: true
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }

                        Rectangle {
                            id: reportListCountBadge
                            width: reportListCountText.implicitWidth + 16
                            height: 20
                            radius: 10
                            color: "#132942"
                            border.color: "#416A92"
                            border.width: 1
                            visible: reportListCountText.text.length > 0

                            Text {
                                id: reportListCountText
                                anchors.centerIn: parent
                                text: root.reportListCountText()
                                color: "#AEEBFF"
                                font.pixelSize: Math.max(9, root.widgetMetaPixelSize)
                                font.bold: true
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: "#20354C"
                        opacity: 0.75
                    }

                    Item {
                        id: reportListViewport
                        width: parent.width
                        height: Math.max(1, parent.height - 34)
                        clip: true

                        Flickable {
                            id: reportListFlick
                            anchors.fill: parent
                            anchors.rightMargin: reportListScrollBar.visible ? 10 : 0
                            clip: true
                            contentWidth: width
                            contentHeight: reportListTextBlock.implicitHeight + 4
                            boundsBehavior: Flickable.StopAtBounds
                            flickableDirection: Flickable.VerticalFlick

                            Text {
                                id: reportListTextBlock
                                width: Math.max(1, reportListFlick.width - 6)
                                text: root.reportListPanelText()
                                color: "#DDEBFF"
                                font.pixelSize: Math.max(10, root.widgetMetaPixelSize)
                                lineHeight: 1.18
                                wrapMode: Text.WrapAnywhere
                            }
                        }

                        Rectangle {
                            id: reportListScrollTrack
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.right: parent.right
                            width: 5
                            radius: 3
                            color: "#111D2B"
                            opacity: reportListScrollBar.visible ? 0.9 : 0.0
                        }

                        Rectangle {
                            id: reportListScrollBar
                            anchors.right: parent.right
                            width: 5
                            radius: 3
                            color: reportListFlick.moving || reportListFlick.dragging ? "#8FEAFF" : "#4F789D"
                            opacity: visible ? (reportListFlick.moving || reportListFlick.dragging ? 0.95 : 0.66) : 0.0
                            visible: reportListFlick.contentHeight > reportListFlick.height + 2
                            height: visible ? Math.max(28, reportListViewport.height * reportListFlick.height / Math.max(reportListFlick.contentHeight, 1)) : 0
                            y: visible ? Math.max(0, Math.min(reportListViewport.height - height, reportListFlick.contentY * (reportListViewport.height - height) / Math.max(reportListFlick.contentHeight - reportListFlick.height, 1))) : 0
                        }
                    }
                }
            }

        }

        Item {
            id: feedbackPanel
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 0
            visible: false
            enabled: false
            clip: true

            Rectangle {
                anchors.fill: parent
                radius: Math.max(6, root.cardRadiusValue / 3)
                color: "#0E1622"
                opacity: 0.72
                border.color: root.lastDesktopActionStatus === "error" || root.lastDesktopActionStatus === "missing_bridge" ? "#FF7A7A" : "#2F6B4D"
                border.width: 1
            }

            Text {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                text: "last: " + root.lastDesktopActionId + " · " + root.lastDesktopActionMessage
                color: root.lastDesktopActionStatus === "error" || root.lastDesktopActionStatus === "missing_bridge" ? "#FF9A9A" : "#9BE7C0"
                font.pixelSize: root.feedbackPixelSize
                maximumLineCount: 2
                wrapMode: Text.Wrap
                elide: Text.ElideRight
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Popup {
        id: profilePopup
        width: Math.min(520, Math.max(320, root.width - 16))
        height: Math.min(420, Math.max(260, root.height - 16))
        modal: false
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        x: Math.max(8, Math.min((root.width - width) / 2, root.width - width - 8))
        y: 8

        Rectangle {
            anchors.fill: parent
            radius: Math.max(16, root.cardRadiusValue)
            color: "#111824"
            border.color: "#5D8CFF"
            border.width: 2

            ScrollView {
                anchors.fill: parent
                anchors.margins: 14
                clip: true
                contentWidth: Math.max(1, profilePopup.width - 42)
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                    width: 7
                    padding: 1
                    contentItem: Rectangle {
                        implicitWidth: 7
                        radius: 4
                        color: parent.pressed ? "#AEEBFF" : "#4B6A86"
                        opacity: parent.active ? 0.72 : 0.34
                    }
                    background: Rectangle { color: "transparent" }
                }


                Column {
                    width: Math.max(1, profilePopup.width - 28)
                    spacing: 8

                    Text { text: "User Profile"; color: "#EAF2FF"; font.pixelSize: Math.max(16, root.titlePixelSize); font.bold: true; width: parent.width; elide: Text.ElideRight }
                    Text { text: "User: " + root.profileValue("current_user_id", root.sourceValue("controlStateJson.current_user_id", "n/a")); color: "#9BE7C0"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Profile loaded: " + root.profileValue("profile_loaded", root.sourceValue("controlStateJson.profile_loaded", "false")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Last calibration: " + root.profileValue("last_calibration_id", root.sourceValue("controlStateJson.last_calibration_id", "n/a")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Attention low/high: " + root.profileValue("attention_low_threshold", root.sourceValue("controlStateJson.attention_low_threshold", "n/a")) + " / " + root.profileValue("attention_high_threshold", root.sourceValue("controlStateJson.attention_high_threshold", "n/a")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Attention baseline: " + root.profileValue("attention_baseline", root.sourceValue("controlStateJson.attention_baseline", "n/a")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Calibration usable: " + root.profileValue("calibration_usable", root.sourceValue("controlStateJson.calibration_usable", "n/a")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Gyro noise RMS: " + root.profileValue("gyro_noise_rms", root.sourceValue("controlStateJson.gyro_noise_rms", "n/a")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Preferred game: " + root.profileValue("preferred_game_id", root.sourceValue("controlStateJson.preferred_game_id", "n/a")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }

                    ConfigButtonWidget {
                        width: parent.width
                        buttonWidth: parent.width
                        buttonHeight: root.buttonHeight
                        label: "Close Profile Card"
                        actionId: "close_profile_popup"
                        variant: "secondary"
                        onActionRequested: function(actionId) { profilePopup.close() }
                    }
                }
            }
        }
    }



    Popup {
        id: calibrationPopup
        width: Math.min(620, Math.max(340, root.width - 16))
        height: Math.min(520, Math.max(300, root.height - 16))
        modal: false
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        x: Math.max(8, Math.min((root.width - width) / 2, root.width - width - 8))
        y: Math.max(8, Math.min(8, root.height - height - 8))
        padding: 0

        background: Rectangle {
            color: "transparent"
            border.width: 0
        }

        contentItem: Rectangle {
            radius: Math.max(16, root.cardRadiusValue)
            color: "#111824"
            border.color: "#FF6680"
            border.width: 2
            clip: true

            ScrollView {
                anchors.fill: parent
                anchors.margins: 14
                clip: true
                contentWidth: Math.max(1, calibrationPopup.width - 42)
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                    width: 7
                    padding: 1
                    contentItem: Rectangle {
                        implicitWidth: 7
                        radius: 4
                        color: parent.pressed ? "#AEEBFF" : "#4B6A86"
                        opacity: parent.active ? 0.72 : 0.34
                    }
                    background: Rectangle { color: "transparent" }
                }


                Column {
                    width: Math.max(1, calibrationPopup.width - 28)
                    spacing: 8

                    Text { text: "Calibration Detail"; color: "#EAF2FF"; font.pixelSize: Math.max(16, root.titlePixelSize); font.bold: true; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Calibration ID: " + root.calibrationValue("calibration_id", root.sourceValue("controlStateJson.calibration_id", "n/a")); color: "#9BE7C0"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "User: " + root.calibrationValue("user_id", root.sourceValue("controlStateJson.current_user_id", "n/a")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Device: " + root.calibrationValue("device_id", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Created: " + root.calibrationValue("created_at", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Type: " + root.calibrationValue("calibration_type", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Source: " + root.calibrationValue("source", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Attention baseline: " + root.calibrationValue("attention_baseline", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Attention std: " + root.calibrationValue("attention_std", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Attention valid sample ratio: " + root.calibrationValue("attention_valid_sample_ratio", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Gyro bias x/y/z: " + root.calibrationValue("gyro_bias_x", "n/a") + " / " + root.calibrationValue("gyro_bias_y", "n/a") + " / " + root.calibrationValue("gyro_bias_z", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Gyro noise x/y/z: " + root.calibrationValue("gyro_noise_x", "n/a") + " / " + root.calibrationValue("gyro_noise_y", "n/a") + " / " + root.calibrationValue("gyro_noise_z", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Gyro noise RMS: " + root.calibrationValue("gyro_noise_rms", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Gyro stability score: " + root.calibrationValue("gyro_stability_score", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Signal quality baseline: " + root.calibrationValue("signal_quality_baseline", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Valid: " + root.calibrationValue("valid", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Failure reason: " + root.calibrationValue("failure_reason", ""); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Status: " + root.calibrationValue("status", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }
                    Text { text: "Message: " + root.calibrationValue("message", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; width: parent.width; elide: Text.ElideRight }

                    ConfigButtonWidget {
                        width: parent.width
                        buttonWidth: parent.width
                        buttonHeight: root.buttonHeight
                        label: "Close Calibration Card"
                        actionId: "close_calibration_popup"
                        variant: "secondary"
                        onActionRequested: function(actionId) { calibrationPopup.close() }
                    }
                }
            }
        }
    }



    function popupHostWidth() {
        return (Overlay.overlay && Overlay.overlay.width > 0) ? Overlay.overlay.width : root.width
    }

    function popupHostHeight() {
        return (Overlay.overlay && Overlay.overlay.height > 0) ? Overlay.overlay.height : root.height
    }

    Popup {
        id: reportPopup
        parent: Overlay.overlay
        width: Math.max(360, Math.min(860, root.popupHostWidth() - 32))
        height: Math.max(340, Math.min(660, root.popupHostHeight() - 32))
        modal: false
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        x: Math.max(16, Math.min((root.popupHostWidth() - width) / 2, root.popupHostWidth() - width - 16))
        y: Math.max(16, Math.min((root.popupHostHeight() - height) / 2, root.popupHostHeight() - height - 16))
        padding: 0

        background: Rectangle {
            color: "transparent"
            border.width: 0
        }

        contentItem: Rectangle {
            radius: Math.max(18, root.cardRadiusValue)
            color: "#101722"
            border.color: "#6EE7F9"
            border.width: 2
            clip: true

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 10

                Row {
                    width: parent.width
                    height: Math.max(32, root.buttonHeight)
                    spacing: 10

                    Column {
                        width: parent.width - closeReportPopupButton.width - 10
                        spacing: 2
                        Text {
                            text: "Report Detail"
                            color: "#EAF2FF"
                            font.pixelSize: Math.max(17, root.titlePixelSize)
                            font.bold: true
                            width: parent.width
                            elide: Text.ElideRight
                        }
                        Text {
                            text: root.reportValue("session_id", root.reportValue("latest_session_id", "n/a")) + " · " + root.reportValue("status", "n/a")
                            color: "#9BE7C0"
                            font.pixelSize: Math.max(10, root.widgetMetaPixelSize)
                            width: parent.width
                            elide: Text.ElideRight
                        }
                    }

                    ConfigButtonWidget {
                        id: closeReportPopupButton
                        width: 92
                        buttonWidth: 92
                        buttonHeight: root.buttonHeight
                        label: "Close"
                        actionId: "close_report_popup"
                        variant: "secondary"
                        onActionRequested: function(actionId) { reportPopup.close() }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: Math.max(104, Math.min(142, parent.height * 0.25))
                    radius: 14
                    color: "#121C2B"
                    border.color: "#24364F"
                    border.width: 1
                    clip: true

                    Grid {
                        anchors.fill: parent
                        anchors.margins: 10
                        columns: 2
                        rowSpacing: 6
                        columnSpacing: 14

                        Text { width: (parent.width - 14) / 2; text: "User: " + root.reportValue("user_id", root.sourceValue("controlStateJson.current_user_id", "n/a")); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; elide: Text.ElideRight }
                        Text { width: (parent.width - 14) / 2; text: "Game: " + root.reportValue("game_id", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; elide: Text.ElideRight }
                        Text { width: (parent.width - 14) / 2; text: "Score: " + root.reportValue("score", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; elide: Text.ElideRight }
                        Text { width: (parent.width - 14) / 2; text: "Duration: " + root.reportValue("duration_sec", "n/a") + " sec"; color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; elide: Text.ElideRight }
                        Text { width: (parent.width - 14) / 2; text: "Samples: " + root.reportValue("behavior_sample_count", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; elide: Text.ElideRight }
                        Text { width: (parent.width - 14) / 2; text: "Events: " + root.reportValue("game_event_count", "n/a"); color: "#DDEBFF"; font.pixelSize: root.widgetValuePixelSize; elide: Text.ElideRight }
                    }
                }

                Column {
                    width: parent.width
                    spacing: 6

                    Text { text: "Report path"; color: "#8EA4BF"; font.pixelSize: root.widgetMetaPixelSize; width: parent.width }
                    Text {
                        text: root.reportValue("report_path", root.reportValue("latest_report_path", root.sourceValue("controlStateJson.report_selected_report_path", root.sourceValue("controlStateJson.latest_report_path", "n/a"))))
                        color: "#DDEBFF"
                        font.pixelSize: Math.max(10, root.widgetMetaPixelSize)
                        width: parent.width - 14
                        wrapMode: Text.WrapAnywhere
                    }
                    Text { text: "Export path"; color: "#8EA4BF"; font.pixelSize: root.widgetMetaPixelSize; width: parent.width }
                    Text {
                        text: root.reportValue("export_path", root.sourceValue("controlStateJson.report_export_path", "n/a"))
                        color: "#6EE7F9"
                        font.pixelSize: Math.max(10, root.widgetMetaPixelSize)
                        width: parent.width - 14
                        wrapMode: Text.WrapAnywhere
                    }
                }

                Rectangle {
                    width: parent.width
                    height: Math.max(120, parent.height - 306)
                    radius: 14
                    color: "#0B111B"
                    border.color: "#24364F"
                    border.width: 1
                    clip: true

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6

                        Text {
                            text: "Report Preview"
                            color: "#EAF2FF"
                            font.pixelSize: Math.max(14, root.widgetValuePixelSize)
                            font.bold: true
                            width: parent.width
                        }

                        ScrollView {
                            width: parent.width
                            height: parent.height - 28
                            clip: true
                            contentWidth: Math.max(1, width - 16)
                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                            ScrollBar.vertical: ScrollBar {
                                policy: ScrollBar.AsNeeded
                                width: 7
                                padding: 1
                                contentItem: Rectangle {
                                    implicitWidth: 7
                                    radius: 4
                                    color: parent.pressed ? "#AEEBFF" : "#4B6A86"
                                    opacity: parent.active ? 0.72 : 0.34
                                }
                                background: Rectangle { color: "transparent" }
                            }

                            Text {
                                width: Math.max(1, parent.width - 18)
                                text: root.reportValue("report_preview", "n/a")
                                color: "#DDEBFF"
                                font.pixelSize: Math.max(10, root.widgetMetaPixelSize)
                                lineHeight: 1.18
                                wrapMode: Text.WrapAnywhere
                            }
                        }
                    }
                }
            }
        }
    }


}
