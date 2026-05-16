import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 1200
    height: 760
    title: "RELIC Core"
    color: "#101418"

    property color colorText: "#eef3f8"
    property color colorMuted: "#aeb8c2"

    property var appStateObj: null
    property var runtimeObj: null
    property var sessionObj: null
    property var gameHudObj: null
    property var controlManifestObj: null
    property var controlStateObj: null

    function safeJsonParse(jsonText) {
        try { return JSON.parse(jsonText || "{}") }
        catch (e) { return ({"__parse_error__": "invalid"}) }
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
        function onStateChanged() { pullState() }
    }

    Connections { target: guiBridge ? guiBridge : null; function onStateChanged() { pullState() } }
    Component.onCompleted: pullState()

    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 6

        Label { text: "RELIC Core / Developer Diagnostics Console"; color: colorText; font.pixelSize: 22; font.bold: true }
        Label { text: "QML smoke shell loaded"; color: colorMuted; font.pixelSize: 13 }

        Row {
            width: parent.width
            spacing: 8

            Column {
                width: parent.width * 0.34
                spacing: 6

                GroupBox {
                    width: parent.width
                    title: "Control Panel"
                    Column {
                        spacing: 3
                        Label { text: "controlManifestJson parse: " + safeText(getField(controlManifestObj, "__parse_error__", "ok")); color: colorText }
                        Label { text: "control_enabled: " + safeText(getField(controlStateObj, "control_enabled")); color: colorText }
                        Label { text: "readonly: " + safeText(getField(controlStateObj, "readonly")); color: colorText }
                        Label { text: "last_command: " + safeText(getField(controlStateObj, "last_command")); color: colorText }
                        Label { text: "last_command_result: " + safeText(getField(controlStateObj, "last_command_result")); color: colorText }
                        Label { text: "last_command_error: " + safeText(getField(controlStateObj, "last_command_error")); color: colorText }
                        Label { text: "command_count: " + safeText(getField(controlStateObj, "command_count")); color: colorText }

                        Row {
                            spacing: 4
                            Button { text: "Refresh"; onClicked: if (guiBridge) guiBridge.invokeAction("app.refresh_now", "{}") }
                            Button { text: "Reconnect"; onClicked: if (guiBridge) guiBridge.invokeAction("live.reconnect", "{}") }
                            Button { text: "Safe Stop"; onClicked: if (guiBridge) guiBridge.invokeAction("live.safe_stop", "{}") }
                        }
                        Row {
                            spacing: 4
                            Button { text: "Load Current User"; onClicked: if (guiBridge) guiBridge.invokeAction("user.load_current", "{}") }
                            Button { text: "Ensure Demo (Debug)"; onClicked: if (guiBridge) guiBridge.invokeAction("user.ensure_demo_debug", "{}") }
                            Button { text: "Show Profile"; onClicked: if (guiBridge) guiBridge.invokeAction("user.show_profile", "{}") }
                        }
                        Row {
                            spacing: 4
                            Button { text: "Start Session"; onClicked: if (guiBridge) guiBridge.invokeAction("session.start", "{}") }
                            Button { text: "Stop Session"; onClicked: if (guiBridge) guiBridge.invokeAction("session.stop", "{}") }
                            Button { text: "Session Status"; onClicked: if (guiBridge) guiBridge.invokeAction("session.status", "{}") }
                            Button { text: "Game Status"; onClicked: if (guiBridge) guiBridge.invokeAction("game.status", "{}") }
                        }
                        Row {
                            spacing: 4
                            Button { text: "Calibration Status"; onClicked: if (guiBridge) guiBridge.invokeAction("calibration.status", "{}") }
                            Button { text: "Start Calibration"; onClicked: if (guiBridge) guiBridge.invokeAction("calibration.start", "{}") }
                        }
                    }
                }

                GroupBox {
                    width: parent.width
                    title: "Profile / Calibration"
                    Column {
                        spacing: 3
                        Label { text: "current_user_id: " + safeText(getField(controlStateObj, "current_user_id")); color: colorText }
                        Label { text: "user_type: " + safeText(getField(controlStateObj, "user_type")); color: colorText }
                        Label { text: "profile_status: " + safeText(getField(controlStateObj, "profile_status")); color: colorText }
                        Label { text: "profile_loaded: " + safeText(getField(controlStateObj, "profile_loaded")); color: colorText }
                        Label { text: "calibration_status: " + safeText(getField(controlStateObj, "calibration_status")); color: colorText }
                        Label { text: "calibration_usable: " + safeText(getField(controlStateObj, "calibration_usable")); color: colorText }
                        Label { text: "last_calibration_id: " + safeText(getField(controlStateObj, "last_calibration_id")); color: colorText }
                    }
                }
            }

            Column {
                width: parent.width * 0.31
                spacing: 6

                GroupBox {
                    width: parent.width
                    title: "Connection"
                    Column {
                        spacing: 3
                        Label { text: "connection_status: " + safeText(getField(runtimeObj, "connection_status")); color: colorText }
                        Label { text: "stream_alive: " + safeText(getField(runtimeObj, "stream_alive")); color: colorText }
                        Label { text: "device_connected: " + safeText(getField(runtimeObj, "device_connected")); color: colorText }
                    }
                }

                GroupBox {
                    width: parent.width
                    title: "Attention"
                    Column {
                        spacing: 3
                        Label { text: "attention: " + safeText(getField(runtimeObj, "attention")); color: colorText }
                        Label { text: "attention_fresh: " + safeText(getField(runtimeObj, "attention_fresh")); color: colorText }
                        Label { text: "attention_age_ms: " + safeText(getField(runtimeObj, "attention_age_ms")); color: colorText }
                        Label { text: "attention_last_update_ms: " + safeText(getField(runtimeObj, "attention_last_update_ms")); color: colorText }
                    }
                }

                GroupBox {
                    width: parent.width
                    title: "Gyroscope"
                    Column {
                        spacing: 3
                        Label { text: "gyro_x: " + safeText(getField(runtimeObj, "gyro_x")); color: colorText }
                        Label { text: "gyro_y: " + safeText(getField(runtimeObj, "gyro_y")); color: colorText }
                        Label { text: "gyro_z: " + safeText(getField(runtimeObj, "gyro_z")); color: colorText }
                        Label { text: "gyro_fresh: " + safeText(getField(runtimeObj, "gyro_fresh")); color: colorText }
                        Label { text: "gyro_age_ms: " + safeText(getField(runtimeObj, "gyro_age_ms")); color: colorText }
                        Label { text: "gyro_last_update_ms: " + safeText(getField(runtimeObj, "gyro_last_update_ms")); color: colorText }
                    }
                }
            }

            Column {
                width: parent.width * 0.33
                spacing: 6

                GroupBox {
                    width: parent.width
                    title: "Runtime Snapshot"
                    Label { text: "Quality / Focus (TASK6)"; visible: false }
                    Label { text: "Live Input"; visible: false }
                    Column {
                        spacing: 3
                        Label { text: "mode: " + safeText(getField(appStateObj, "mode")); color: colorText }
                        Label { text: "source: " + safeText(getField(appStateObj, "source")); color: colorText }
                        Label { text: "sqi: " + safeText(getField(runtimeObj, "sqi")); color: colorText }
                        Label { text: "quality_state: " + safeText(getField(runtimeObj, "quality_state")); color: colorText }
                        Label { text: "fi_smoothed: " + safeText(getField(runtimeObj, "fi_smoothed", getField(runtimeObj, "fi"))); color: colorText }
                        Label { text: "fi_valid: " + safeText(getField(runtimeObj, "fi_valid")); color: colorText }
                        Label { text: "control_state: " + safeText(getField(runtimeObj, "control_state")); color: colorText }
                        Label { text: "control_state_reason: " + safeText(getField(runtimeObj, "control_state_reason")); color: colorText }
                    }
                }

                GroupBox {
                    width: parent.width
                    title: "Session"
                    Column {
                        spacing: 3
                        Label { text: "session_type: " + safeText(getField(sessionObj, "session_type")); color: colorText }
                        Label { text: "session_id: " + safeText(getField(sessionObj, "session_id")); color: colorText }
                        Label { text: "session_active: " + safeText(getField(controlStateObj, "session_active")); color: colorText }
                        Label { text: "current_session_id: " + safeText(getField(controlStateObj, "current_session_id")); color: colorText }
                        Label { text: "session_elapsed_ms: " + safeText(getField(controlStateObj, "session_elapsed_ms")); color: colorText }
                        Label { text: "latest_report_path: " + safeText(getField(controlStateObj, "latest_report_path")); color: colorText }
                    }
                }

                GroupBox {
                    width: parent.width
                    title: "Diagnostics / Game HUD"
                    Column {
                        spacing: 3
                        Label { text: "warning_flags: " + safeText(JSON.stringify(getField(runtimeObj, "warning_flags", getField(runtimeObj, "current_warning_flags", "n/a")))); color: colorText }
                        Label { text: "error_flags: " + safeText(JSON.stringify(getField(runtimeObj, "error_flags", "n/a"))); color: colorText }
                        Label { text: "game_id: " + safeText(getField(controlStateObj, "current_game_id", getField(sessionObj, "game_id"))); color: colorText }
                        Label { text: "score: " + safeText(getField(gameHudObj, "score")); color: colorText }
                        Label { text: "behavior_sample_count: " + safeText(getField(sessionObj, "behavior_sample_count")); color: colorText }
                        Label { text: "combo: " + safeText(getField(gameHudObj, "combo")); color: colorText }
                        Label { text: "level: " + safeText(getField(gameHudObj, "level")); color: colorText }
                    }
                }
            }
        }
    }
}

// tokens: Game HUD Game Status
// token: command_count
