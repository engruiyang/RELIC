import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 1000
    height: 700
    title: "RELIC Core"

    color: "#101418"
    property color colorPanel: "#1b222a"
    property color colorText: "#eef3f8"
    property color colorMuted: "#aeb8c2"

    property var appStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameHudObj: ({})
    property var controlManifestObj: ([])
    property var controlStateObj: ({})

    function safeJsonParse(jsonText) {
        try {
            return JSON.parse(jsonText || "{}")
        } catch (e) {
            return ({"__parse_error__": "invalid"})
        }
    }

    function safeText(value, fallback) {
        var fb = fallback === undefined ? "n/a" : fallback
        return value === undefined || value === null || value === "" ? fb : String(value)
    }

    function getField(obj, key, fallback) {
        if (!obj || obj[key] === undefined || obj[key] === null || obj[key] === "") {
            return fallback === undefined ? "n/a" : fallback
        }
        return obj[key]
    }

    function pullState() {
        if (!guiBridge) {
            appStateObj = ({})
            runtimeObj = ({})
            sessionObj = ({})
            gameHudObj = ({})
            controlManifestObj = ([])
            controlStateObj = ({})
            return
        }
        appStateObj = safeJsonParse(guiBridge.appState)
        runtimeObj = safeJsonParse(guiBridge.runtimeSnapshot)
        sessionObj = safeJsonParse(guiBridge.sessionState)
        gameHudObj = safeJsonParse(guiBridge.gameHudJson)
        controlManifestObj = safeJsonParse(guiBridge.controlManifestJson)
        controlStateObj = safeJsonParse(guiBridge.controlStateJson)
    }

    Connections {
        target: guiBridge ? guiBridge : null
        function onStateChanged() {
            pullState()
        }
    }

    Component.onCompleted: pullState()

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 8

        Label { text: "RELIC Core / Developer Diagnostics Console"; color: colorText; font.pixelSize: 24; font.bold: true }
        Label { text: "QML smoke shell loaded"; color: colorMuted; font.pixelSize: 16 }


        GroupBox {
            width: parent.width
            title: "Control Panel"
            Column {
                spacing: 4
                Label { text: "controlManifestJson parse: " + safeText(getField(controlManifestObj, "__parse_error__", "ok"), "ok") }
                Label { text: "control_enabled: " + safeText(getField(controlStateObj, "control_enabled")) }
                Label { text: "readonly: " + safeText(getField(controlStateObj, "readonly")) }
                Label { text: "last_command: " + safeText(getField(controlStateObj, "last_command")) }
                Label { text: "last_command_result: " + safeText(getField(controlStateObj, "last_command_result")) }
                Label { text: "last_command_error: " + safeText(getField(controlStateObj, "last_command_error")) }
                Label { text: "command_count: " + safeText(getField(controlStateObj, "command_count")) }
                Label { text: "app_elapsed_ms: " + safeText(getField(controlStateObj, "app_elapsed_ms")) }
                Label { text: "session_active: " + safeText(getField(controlStateObj, "session_active")); color: colorText }
                Label { text: "session_elapsed_ms: " + safeText(getField(controlStateObj, "session_elapsed_ms")); color: colorText }
                Label { text: "last_session_status: " + safeText(getField(controlStateObj, "last_session_status")); color: colorText }
                Label { text: "current_user_id: " + safeText(getField(controlStateObj, "current_user_id")) }
                Label { text: "current_session_id: " + safeText(getField(controlStateObj, "current_session_id")) }
                Label { text: "current_game_id: " + safeText(getField(controlStateObj, "current_game_id")) }
                Label { text: "latest_report_path: " + safeText(getField(controlStateObj, "latest_report_path")); color: colorText }
                Label { text: "user_type: " + safeText(getField(controlStateObj, "user_type")); color: colorText }
                Label { text: "profile_loaded: " + safeText(getField(controlStateObj, "profile_loaded")); color: colorText }
                Label { text: "last_calibration_id: " + safeText(getField(controlStateObj, "last_calibration_id")); color: colorText }
                Label { text: "calibration_status: " + safeText(getField(controlStateObj, "calibration_status")); color: colorText }
                Label { text: "calibration_usable: " + safeText(getField(controlStateObj, "calibration_usable")); color: colorText }

                Row { spacing: 6
                    Button { text: "Refresh"; onClicked: if (guiBridge) { guiBridge.invokeAction("app.refresh_now", "{}") } }
                    Button { text: "Quit"; onClicked: if (guiBridge) { guiBridge.invokeAction("app.quit", "{}") } }
                    Button { text: "Reconnect"; onClicked: if (guiBridge) { guiBridge.invokeAction("live.reconnect", "{}") } }
                    Button { text: "Safe Stop"; onClicked: if (guiBridge) { guiBridge.invokeAction("live.safe_stop", "{}") } }
                }
                Row { spacing: 6
                    Button { text: "Ensure Demo User"; onClicked: if (guiBridge) { guiBridge.invokeAction("user.ensure_demo", "{}") } }
                    Button { text: "Show Profile"; onClicked: if (guiBridge) { guiBridge.invokeAction("user.show_profile", "{}") } }
                    Button { text: "Start Calibration"; onClicked: if (guiBridge) { guiBridge.invokeAction("calibration.start", "{}") } }
                    Button { text: "Calibration Status"; onClicked: if (guiBridge) { guiBridge.invokeAction("calibration.status", "{}") } }
                }
                Row { spacing: 6
                    Button { text: "Start Session"; onClicked: if (guiBridge) { guiBridge.invokeAction("session.start", "{}") } }
                    Button { text: "Stop Session"; onClicked: if (guiBridge) { guiBridge.invokeAction("session.stop", "{}") } }
                    Button { text: "Session Status"; onClicked: if (guiBridge) { guiBridge.invokeAction("session.status", "{}") } }
                    Button { text: "Game Status"; onClicked: if (guiBridge) { guiBridge.invokeAction("game.status", "{}") } }
                }
                Row { spacing: 6
                    Button { text: "Clear Last Error"; onClicked: if (guiBridge) { guiBridge.invokeAction("diagnostics.clear_last_error", "{}") } }
                    Button { text: "Refresh Diagnostics"; onClicked: if (guiBridge) { guiBridge.invokeAction("diagnostics.refresh", "{}") } }
                }
            }
        }


        GroupBox {
            width: parent.width
            title: "Profile"
            Column {
                spacing: 4
                Label { text: "current_user_id: " + safeText(getField(controlStateObj, "current_user_id")); color: colorText }
                Label { text: "user_type: " + safeText(getField(controlStateObj, "user_type")); color: colorText }
                Label { text: "profile_loaded: " + safeText(getField(controlStateObj, "profile_loaded")); color: colorText }
                Label { text: "last_calibration_id: " + safeText(getField(controlStateObj, "last_calibration_id")); color: colorText }
                Label { text: "profile_status: " + safeText(getField(controlStateObj, "profile_status")); color: colorText }
            }
        }

        GroupBox {
            width: parent.width
            title: "Calibration"
            Column {
                spacing: 4
                Label { text: "calibration_status: " + safeText(getField(controlStateObj, "calibration_status")); color: colorText }
                Label { text: "last_calibration_id: " + safeText(getField(controlStateObj, "last_calibration_id")); color: colorText }
                Label { text: "calibration_usable: " + safeText(getField(controlStateObj, "calibration_usable")); color: colorText }
            }
        }

        GroupBox {
            width: parent.width
            title: "Connection"
            Column {
                spacing: 4
                Label { text: "connection_status: " + safeText(getField(runtimeObj, "connection_status")) }
                Label { text: "stream_alive: " + safeText(getField(runtimeObj, "stream_alive")) }
                Label { text: "device_connected: " + safeText(getField(runtimeObj, "device_connected")) }
            }
        }

        GroupBox {
            width: parent.width
            title: "Runtime Snapshot"
            Column {
                spacing: 4
                Label { text: "mode: " + safeText(getField(appStateObj, "mode")) }
                Label { text: "source: " + safeText(getField(appStateObj, "source")) }
                Label { text: "runtime_snapshot_parse: " + safeText(getField(runtimeObj, "__parse_error__", "ok"), "ok") }
                Label { text: "game_hud_parse: " + safeText(getField(gameHudObj, "__parse_error__", "ok"), "ok") }
            }
        }

        GroupBox {
            width: parent.width
            title: "Attention"
            Column {
                spacing: 4
                Label { text: "attention: " + safeText(getField(runtimeObj, "attention")) }
                Label { text: "attention_fresh: " + safeText(getField(runtimeObj, "attention_fresh")) }
                Label { text: "attention_age_ms: " + safeText(getField(runtimeObj, "attention_age_ms")) }
                Label { text: "attention_last_update_ms: " + safeText(getField(runtimeObj, "attention_last_update_ms")) }
            }
        }

        GroupBox {
            width: parent.width
            title: "Gyroscope"
            Column {
                spacing: 4
                Label { text: "gyro_x: " + safeText(getField(runtimeObj, "gyro_x")) }
                Label { text: "gyro_y: " + safeText(getField(runtimeObj, "gyro_y")) }
                Label { text: "gyro_z: " + safeText(getField(runtimeObj, "gyro_z")) }
                Label { text: "gyro_fresh: " + safeText(getField(runtimeObj, "gyro_fresh")) }
                Label { text: "gyro_age_ms: " + safeText(getField(runtimeObj, "gyro_age_ms")) }
                Label { text: "gyro_last_update_ms: " + safeText(getField(runtimeObj, "gyro_last_update_ms")) }
            }
        }

        GroupBox {
            width: parent.width
            title: "Session"
            Column {
                spacing: 4
                Label { text: "session_type: " + safeText(getField(sessionObj, "session_type", getField(sessionObj, "currentSessionType"))) }
                Label { text: "session_id: " + safeText(getField(sessionObj, "session_id")) }
                Label { text: "latest_report_path: " + safeText(getField(sessionObj, "latest_report_path", getField(sessionObj, "report_path"))) }
            }
        }

        GroupBox {
            width: parent.width
            title: "Diagnostics"
            Column {
                spacing: 4
                Label { text: "warning_flags: " + safeText(JSON.stringify(getField(runtimeObj, "warning_flags", getField(runtimeObj, "current_warning_flags", "n/a")))) }
                Label { text: "error_flags: " + safeText(JSON.stringify(getField(runtimeObj, "error_flags", "n/a"))) }
            }
        }

        GroupBox {
            width: parent.width
            title: "Game HUD"
            Column {
                spacing: 4
                Label { text: "score: " + safeText(getField(gameHudObj, "score")) }
                Label { text: "combo: " + safeText(getField(gameHudObj, "combo")) }
                Label { text: "level: " + safeText(getField(gameHudObj, "level")) }
                Label { text: "load_tier: " + safeText(getField(gameHudObj, "load_tier")) }
                Label { text: "movement_type: " + safeText(getField(gameHudObj, "movement_type")) }
                Label { text: "target_time_left_ms: " + safeText(getField(gameHudObj, "target_time_left_ms")) }
            }
        }
    }
}
