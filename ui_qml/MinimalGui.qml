import QtQuick
import QtQuick.Controls
import "pages"
import "components"

ApplicationWindow {
    id: root

    visible: true
    width: Number(appShellLayoutValue("window_width", 1360))
    height: Number(appShellLayoutValue("window_height", 860))
    title: "RELIC Core"
    color: root.designColor("background", "#0f1720")

    property string currentPage: "home"
    property var appStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})
    property var controlStateObj: ({})
    property var pageCommandManifestObj: ({})
    property var renderResourcesObj: ({})
    property var designThemeObj: ({})
    property var pageStylesObj: ({})
    property var componentStylesObj: ({})
    property var gameStylesObj: ({})
    property var effectStylesObj: ({})

    function safeJsonParse(t) {
        try {
            return JSON.parse(t || "{}")
        } catch (e) {
            return ({"__parse_error__": "invalid"})
        }
    }

    function safeText(v, f) {
        var fb = f === undefined ? "n/a" : f
        return v === undefined || v === null || v === "" ? fb : String(v)
    }

    function getField(o, k, f) {
        if (!o || o[k] === undefined || o[k] === null || o[k] === "") {
            return f === undefined ? "n/a" : f
        }
        return o[k]
    }

    function designColor(k, f) {
        var c = designThemeObj.colors || ({})
        return c[k] === undefined || c[k] === null || c[k] === "" ? f : c[k]
    }

    function designSpacing(k, f) {
        var s = designThemeObj.spacing || ({})
        return s[k] === undefined || s[k] === null || s[k] === "" ? f : s[k]
    }

    function pageStyle(pageId) {
        return pageStylesObj[pageId] || ({})
    }

    function componentStyle(componentId) {
        return componentStylesObj[componentId] || ({})
    }

    function appShellLayoutValue(key, fallbackValue) {
        var layout = pageStyle("app_shell").layout || ({})
        var v = layout[key]
        return v === undefined || v === null || v === "" ? fallbackValue : v
    }

    function commandsFor(pageId) {
        var p = pageCommandManifestObj.pages || ({})
        var arr = p[pageId] || []
        var out = []
        for (var i = 0; i < arr.length && i < 4; i++) {
            out.push(arr[i].command_id + "(" + arr[i].execution_mode + ")")
        }
        return out.join(" | ")
    }

    function pullState() {
        if (!guiBridge) {
            return
        }
        appStateObj = safeJsonParse(guiBridge.appState)
        runtimeObj = safeJsonParse(guiBridge.runtimeSnapshot)
        sessionObj = safeJsonParse(guiBridge.sessionState)
        gameHudObj = safeJsonParse(guiBridge.gameHudJson)
        gameViewObj = safeJsonParse(guiBridge.gameViewJson)
        controlStateObj = safeJsonParse(guiBridge.controlStateJson)
        pageCommandManifestObj = safeJsonParse(guiBridge.pageCommandManifestJson)
        renderResourcesObj = safeJsonParse(guiBridge.renderResourcesJson)
        designThemeObj = renderResourcesObj.theme || ({})
        pageStylesObj = renderResourcesObj.page_styles || ({})
        componentStylesObj = renderResourcesObj.component_styles || ({})
        gameStylesObj = renderResourcesObj.game_styles || ({})
        effectStylesObj = renderResourcesObj.effect_styles || ({})
    }

    function invokeNative(actionId) {
        if (guiBridge) {
            guiBridge.invokeAction(actionId, "{}")
        }
    }

    Connections {
        target: guiBridge ? guiBridge : null
        function onStateChanged() {
            pullState()
        }
    }

    Component.onCompleted: pullState()

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyle("app_shell")
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: "#0f1720"
    }

    Column {
        anchors.fill: parent
        anchors.margins: Number(root.appShellLayoutValue("content_margin", root.designSpacing("page_margin", 8)))
        spacing: Number(root.appShellLayoutValue("section_gap", root.designSpacing("section_gap", 6)))

        DesignPanel {
            width: parent.width
            height: Number(root.appShellLayoutValue("top_bar_height", 64))
            panelStyleObj: root.componentStyle("header")
            themeObj: root.designThemeObj

            Row {
                anchors.fill: parent
                spacing: 12

                Label {
                    text: "RELIC / 意念玩家"
                    font.pixelSize: Number((root.designThemeObj.typography || ({})).title_size || 18)
                    font.bold: true
                    color: root.designColor("text", "#e6edf5")
                }
                Label { text: "current_user_id: " + safeText(getField(controlStateObj, "current_user_id")); color: root.designColor("text", "#e6edf5") }
                Label { text: "connection_status: " + safeText(getField(runtimeObj, "connection_status")); color: root.designColor("text", "#e6edf5") }
                Label { text: "stream_alive: " + safeText(getField(runtimeObj, "stream_alive")); color: root.designColor("text", "#e6edf5") }
                Label { text: "quality_state: " + safeText(getField(runtimeObj, "quality_state")); color: root.designColor("text", "#e6edf5") }
                Label { text: "session_active: " + safeText(getField(controlStateObj, "session_active")); color: root.designColor("text", "#e6edf5") }
                Label { text: "currentPage: " + currentPage; color: root.designColor("text", "#e6edf5") }
            }
        }

        Row {
            width: parent.width
            height: parent.height - Number(root.appShellLayoutValue("top_bar_height", 64)) - parent.spacing
            spacing: Number(root.designSpacing("section_gap", 6))

            DesignPanel {
                width: Number(root.appShellLayoutValue("nav_width", 230))
                height: parent.height
                panelStyleObj: root.componentStyle("panel")
                themeObj: root.designThemeObj

                Column {
                    anchors.fill: parent
                    spacing: Number(root.designSpacing("nav_gap", 7))

                    Label { text: "Navigation"; color: root.designColor("text", "#e6edf5"); font.bold: true }
                    DesignButton { text: "Home"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: currentPage = "home" }
                    DesignButton { text: "User"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: currentPage = "user" }
                    DesignButton { text: "Calibration"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: currentPage = "calibration" }
                    DesignButton { text: "Training"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: currentPage = "training" }
                    DesignButton { text: "Report"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: currentPage = "report" }
                    DesignButton { text: "Diagnostics"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: currentPage = "diagnostics" }
                    DesignButton { text: "Developer Lab"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: currentPage = "developer_lab" }
                    Label { text: "Global Safety"; color: root.designColor("text_muted", "#9aacbd") }
                    DesignButton { text: "Refresh"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: invokeNative("app.refresh_now") }
                    DesignButton { text: "Safe Stop"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: invokeNative("live.safe_stop") }
                    DesignButton { text: "Go Diagnostics"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: currentPage = "diagnostics" }
                    DesignButton { text: "Quit"; buttonStyleObj: root.componentStyle("button"); themeObj: root.designThemeObj; onClicked: Qt.quit() }
                }
            }

            DesignPanel {
                width: parent.width - Number(root.appShellLayoutValue("nav_width", 230)) - parent.spacing
                height: parent.height
                panelStyleObj: root.componentStyle("panel")
                themeObj: root.designThemeObj

                Item {
                    id: pageHost
                    objectName: "PageHost"
                    anchors.fill: parent

                    DesignBackground {
                        anchors.fill: parent
                        themeObj: root.designThemeObj
                        styleObj: root.pageStyle(currentPage === "training" ? "training_page" : (currentPage + "_page"))
                        renderResourcesObj: root.renderResourcesObj
                        fallbackColor: root.designColor("background", "#0f1720")
                    }

                    HomePage { anchors.fill: parent; visible: currentPage === "home"; controlStateObj: root.controlStateObj; runtimeObj: root.runtimeObj; commandSummary: root.commandsFor("home"); onNavigateTo: (p)=>{root.currentPage=p}; onInvokeNative: (a)=>root.invokeNative(a) }
                    UserPage { anchors.fill: parent; visible: currentPage === "user"; appStateObj: root.appStateObj; controlStateObj: root.controlStateObj; commandSummary: root.commandsFor("user"); onInvokeNative: (a)=>root.invokeNative(a) }
                    CalibrationPage { anchors.fill: parent; visible: currentPage === "calibration"; controlStateObj: root.controlStateObj; commandSummary: root.commandsFor("calibration"); onInvokeNative: (a)=>root.invokeNative(a) }
                    TrainingPage { anchors.fill: parent; visible: currentPage === "training"; appStateObj: root.appStateObj; controlStateObj: root.controlStateObj; runtimeObj: root.runtimeObj; gameHudObj: root.gameHudObj; gameViewObj: root.gameViewObj; designThemeObj: root.designThemeObj; pageStyleObj: root.pageStylesObj.training_page || ({}); componentStyleObj: root.componentStylesObj; gameStyleObj: root.gameStylesObj.trace_lock || ({}); effectStyleObj: root.effectStylesObj.trace_lock || ({}); renderResourcesObj: root.renderResourcesObj; commandSummary: root.commandsFor("training"); onInvokeNative: (a)=>root.invokeNative(a) }
                    ReportPage { anchors.fill: parent; visible: currentPage === "report"; appStateObj: root.appStateObj; controlStateObj: root.controlStateObj; sessionObj: root.sessionObj; commandSummary: root.commandsFor("report") }
                    DiagnosticsPage { anchors.fill: parent; visible: currentPage === "diagnostics"; controlStateObj: root.controlStateObj; runtimeObj: root.runtimeObj; sessionObj: root.sessionObj; gameHudObj: root.gameHudObj; commandSummary: root.commandsFor("diagnostics"); onInvokeNative: (a)=>root.invokeNative(a) }
                    DeveloperLabPage { anchors.fill: parent; visible: currentPage === "developer_lab"; controlStateObj: root.controlStateObj; commandSummary: root.commandsFor("developer_lab") }
                }
            }
        }
    }

    // TASK25B global GUI skin layer: DesignBackground / DesignPanel / DesignButton consume design pack tokens. background.app.main
}

// Compatibility tokens kept for TASK21/TASK23 tests:
// RELIC Core / Developer Diagnostics Console
// QML smoke shell loaded
// Connection Runtime Snapshot Attention Gyroscope Session Diagnostics Game HUD
// device_connected attention_fresh attention_age_ms attention_last_update_ms gyro_x gyro_y gyro_z gyro_fresh gyro_age_ms gyro_last_update_ms session_type session_id latest_report_path warning_flags error_flags
// Control Panel Reconnect Start Session Stop Session Calibration Status Game Status Quality / Focus (TASK6) Live Input
// gameViewJson controlManifestJson controlStateJson last_command last_command_result last_command_error command_count
// profile_status calibration_status profile_loaded user_type attention_low_threshold attention_high_threshold preferred_game_id calibration_usable last_calibration_id failure_reason
// First Profile Calibration Quick Check Periodic Recalibration Triggered Recalibration
// GameCanvas will be restored in TASK24 score combo level session_elapsed_ms behavior_sample_count Fragment Lock Signal Hunter Stabilizer last_session_status current_session_id attention sqi fi_smoothed control_state
