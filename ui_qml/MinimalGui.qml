import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 1360
    height: 860
    title: "RELIC Core"
    color: "#0f1720"

    property string currentPage: "home"
    property color colorText: "#e6edf5"
    property color colorMuted: "#9aacbd"
    property color colorPanel: "#172330"

    property var appStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameHudObj: ({})
    property var controlManifestObj: ([])
    property var controlStateObj: ({})
    property var pageCommandManifestObj: ({})

    function safeJsonParse(jsonText) { try { return JSON.parse(jsonText || "{}") } catch (e) { return ({"__parse_error__":"invalid"}) } }
    function safeText(value, fallback) { var fb = fallback === undefined ? "n/a" : fallback; return value === undefined || value === null || value === "" ? fb : String(value) }
    function getField(obj, key, fallback) { if (!obj || obj[key] === undefined || obj[key] === null || obj[key] === "") return fallback === undefined ? "n/a" : fallback; return obj[key] }
    function invoke(actionId) { if (guiBridge) guiBridge.invokeAction(actionId, "{}") }

    function pullState() {
        if (!guiBridge) return
        appStateObj = safeJsonParse(guiBridge.appState)
        runtimeObj = safeJsonParse(guiBridge.runtimeSnapshot)
        sessionObj = safeJsonParse(guiBridge.sessionState)
        gameHudObj = safeJsonParse(guiBridge.gameHudJson)
        controlManifestObj = safeJsonParse(guiBridge.controlManifestJson)
        controlStateObj = safeJsonParse(guiBridge.controlStateJson)
        pageCommandManifestObj = safeJsonParse(guiBridge.pageCommandManifestJson)
    }

    function nextActionHint() {
        if (safeText(getField(controlStateObj, "current_user_id")) === "n/a") return "Next Action: Load Current User"
        if (safeText(getField(controlStateObj, "profile_status")) !== "ok") return "Next Action: Go User / Profile"
        if (safeText(getField(controlStateObj, "calibration_usable")) !== "true") return "Next Action: Go Calibration"
        if (safeText(getField(runtimeObj, "stream_alive")) !== "true") return "Next Action: Reconnect live source"
        if (safeText(getField(runtimeObj, "quality_state")) !== "usable") return "Next Action: Go Diagnostics"
        return "Next Action: Go Training"
    }

    Connections { target: guiBridge ? guiBridge : null; function onStateChanged() { pullState() } }
    Component.onCompleted: pullState()

    Column {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 6

        Rectangle {
            width: parent.width; height: 60; color: colorPanel; radius: 8
            Row { anchors.fill: parent; anchors.margins: 10; spacing: 16
                Label { text: "RELIC Core / Developer Diagnostics Console"; color: colorText; font.pixelSize: 20; font.bold: true }
                Label { text: "QML smoke shell loaded"; color: colorMuted }
                Label { text: "current_user_id: " + safeText(getField(controlStateObj, "current_user_id")); color: colorText }
                Label { text: "connection_status: " + safeText(getField(runtimeObj, "connection_status")); color: colorText }
                Label { text: "stream_alive: " + safeText(getField(runtimeObj, "stream_alive")); color: colorText }
                Label { text: "quality_state: " + safeText(getField(runtimeObj, "quality_state")); color: colorText }
                Label { text: "control_state: " + safeText(getField(runtimeObj, "control_state")); color: colorText }
                Label { text: "session_active: " + safeText(getField(controlStateObj, "session_active")); color: colorText }
                Label { text: "currentPage: " + currentPage; color: colorText }
            }
        }

        Row {
            width: parent.width; height: parent.height - 70; spacing: 6

            Rectangle {
                width: 210; height: parent.height; color: colorPanel; radius: 8
                Column { anchors.fill: parent; anchors.margins: 8; spacing: 6
                    Label { text: "Task Menu"; color: colorText; font.bold: true }
                    Button { text: "Home"; onClicked: currentPage = "home" }
                    Button { text: "User"; onClicked: currentPage = "user" }
                    Button { text: "Calibration"; onClicked: currentPage = "calibration" }
                    Button { text: "Training"; onClicked: currentPage = "training" }
                    Button { text: "Report"; onClicked: currentPage = "report" }
                    Button { text: "Diagnostics"; onClicked: currentPage = "diagnostics" }
                }
            }

            Rectangle {
                width: 260; height: parent.height; color: colorPanel; radius: 8
                Column { anchors.fill: parent; anchors.margins: 8; spacing: 6
                    Label { text: "Control Panel"; color: colorText; font.bold: true }
                    Button { text: "Refresh"; onClicked: invoke("app.refresh_now") }
                    Button { text: "Load Current User"; onClicked: invoke("user.load_current") }
                    Button { text: "Show Profile"; onClicked: invoke("user.show_profile") }
                    Button { text: "Calibration Status"; onClicked: invoke("calibration.status") }
                    Button { text: "Start Session"; enabled: safeText(getField(controlStateObj, "readonly")) !== "true"; onClicked: invoke("session.start") }
                    Button { text: "Stop Session"; enabled: safeText(getField(controlStateObj, "readonly")) !== "true"; onClicked: invoke("session.stop") }
                    Button { text: "Safe Stop"; onClicked: invoke("live.safe_stop") }
                    Button { text: "Reconnect"; onClicked: invoke("live.reconnect") }
                    Button { text: "Game Status"; onClicked: invoke("game.status") }
                    Button { text: "Quit"; onClicked: Qt.quit() }
                    Label { text: "Start Calibration: not_implemented"; color: colorMuted }
                }
            }

            Rectangle {
                width: parent.width - 210 - 260 - 280; height: parent.height; color: colorPanel; radius: 8
                Column { anchors.fill: parent; anchors.margins: 8; spacing: 6
                    Label { text: "Main Content"; color: colorText; font.bold: true }

                    Column { visible: currentPage === "home"; spacing: 4
                        Label { text: "Home"; color: colorText; font.pixelSize: 18; font.bold: true }
                        Label { text: nextActionHint(); color: colorMuted }
                        Label { text: "profile_status: " + safeText(getField(controlStateObj, "profile_status")); color: colorText }
                        Label { text: "calibration_status: " + safeText(getField(controlStateObj, "calibration_status")); color: colorText }
                        Label { text: "calibration_usable: " + safeText(getField(controlStateObj, "calibration_usable")); color: colorText }
                        Label { text: "attention_fresh: " + safeText(getField(runtimeObj, "attention_fresh")); color: colorText }
                        Label { text: "gyro_fresh: " + safeText(getField(runtimeObj, "gyro_fresh")); color: colorText }
                        Label { text: "latest_report_path: " + safeText(getField(controlStateObj, "latest_report_path")); color: colorText }
                    }
                    Column { visible: currentPage === "user"; spacing: 4
                        Label { text: "User / Profile"; color: colorText; font.pixelSize: 18; font.bold: true }
                        Label { text: "Page Commands: user.*"; color: colorMuted }
                        Label { text: "user_type: " + safeText(getField(controlStateObj, "user_type")); color: colorText }
                        Label { text: "profile_loaded: " + safeText(getField(controlStateObj, "profile_loaded")); color: colorText }
                        Label { text: "last_calibration_id: " + safeText(getField(controlStateObj, "last_calibration_id")); color: colorText }
                        Label { text: "attention_low_threshold: " + safeText(getField(controlStateObj, "attention_low_threshold")); color: colorText }
                        Label { text: "attention_high_threshold: " + safeText(getField(controlStateObj, "attention_high_threshold")); color: colorText }
                        Label { text: "preferred_game_id: " + safeText(getField(controlStateObj, "preferred_game_id")); color: colorText }
                        Label { text: "difficulty_level: " + safeText(getField(controlStateObj, "difficulty_level")); color: colorText }
                        Label { text: "Full user registration/login page will be expanded later."; color: colorMuted }
                    }
                    Column { visible: currentPage === "calibration"; spacing: 4
                        Label { text: "Calibration"; color: colorText; font.pixelSize: 18; font.bold: true }
                        Label { text: "Page Commands: calibration.*"; color: colorMuted }
                        Label { text: "latest_valid: " + safeText(getField(controlStateObj, "latest_valid")); color: colorText }
                        Label { text: "failure_reason: " + safeText(getField(controlStateObj, "failure_reason")); color: colorText }
                        Label { text: "source: " + safeText(getField(controlStateObj, "source")); color: colorText }
                        Label { text: "attention_baseline: " + safeText(getField(controlStateObj, "attention_baseline")); color: colorText }
                        Label { text: "gyro_noise_rms: " + safeText(getField(controlStateObj, "gyro_noise_rms")); color: colorText }
                        Label { text: "First Profile Calibration (coming soon)"; color: colorMuted }
                        Label { text: "Quick Check (coming soon)"; color: colorMuted }
                        Label { text: "Periodic Recalibration (coming soon)"; color: colorMuted }
                        Label { text: "Triggered Recalibration (coming soon)"; color: colorMuted }
                    }
                    Column { visible: currentPage === "training"; spacing: 4
                        Label { text: "Training"; color: colorText; font.pixelSize: 18; font.bold: true }
                        Label { text: "Page Commands: training.* / game.*"; color: colorMuted }
                        Label { text: "selected_game_id: " + safeText(getField(controlStateObj, "selected_game_id", getField(controlStateObj, "current_game_id"))); color: colorText }
                        Label { text: "fi_smoothed: " + safeText(getField(runtimeObj, "fi_smoothed")); color: colorText }
                        Label { text: "score: " + safeText(getField(gameHudObj, "score")); color: colorText }
                        Label { text: "combo: " + safeText(getField(gameHudObj, "combo")); color: colorText }
                        Label { text: "level: " + safeText(getField(gameHudObj, "level")); color: colorText }
                        Label { text: "score_update_count: " + safeText(getField(gameHudObj, "score_update_count")); color: colorText }
                        Label { text: "feedback_hint: " + safeText(getField(gameHudObj, "feedback_hint")); color: colorText }
                        Label { text: "GameCanvas will be restored in TASK24"; color: colorMuted }
                        Label { text: "Fragment Lock (reference ready)"; color: colorText }
                        Label { text: "Signal Hunter (planned)"; color: colorMuted }
                        Label { text: "Stabilizer (planned)"; color: colorMuted }
                    }
                    Column { visible: currentPage === "report"; spacing: 4
                        Label { text: "Report"; color: colorText; font.pixelSize: 18; font.bold: true }
                        Label { text: "Page Commands: report.*"; color: colorMuted }
                        Label { text: "last_session_status: " + safeText(getField(controlStateObj, "last_session_status")); color: colorText }
                        Label { text: "report_status: " + safeText(getField(controlStateObj, "report_status")); color: colorText }
                        Label { text: "log_path: " + safeText(getField(controlStateObj, "log_path")); color: colorText }
                        Label { text: "game_event_count: " + safeText(getField(controlStateObj, "game_event_count")); color: colorText }
                        Label { text: "Full report viewer and report enhancement will be handled in later tasks."; color: colorMuted }
                    }
                    Column { visible: currentPage === "diagnostics"; spacing: 2
                        Label { text: "Diagnostics"; color: colorText; font.pixelSize: 18; font.bold: true }
                        Label { text: "Page Commands: runtime.* / diagnostics.*"; color: colorMuted }
                        Label { text: "Developer Lab: developer.task6b_* / game.debug_*"; color: colorMuted }
                        Label { text: "Connection / Runtime"; color: colorMuted }
                        Label { text: "Attention"; color: colorMuted }
                        Label { text: "Gyroscope"; color: colorMuted }
                        Label { text: "Session"; color: colorMuted }
                        Label { text: "Game HUD"; color: colorMuted }
                        Label { text: "Quality / Focus (TASK6)"; color: colorMuted }
                        Label { text: "Live Input"; color: colorMuted }
                        Label { text: "sqi: " + safeText(getField(runtimeObj, "sqi")); color: colorText }
                        Label { text: "quality_reasons: " + safeText(getField(runtimeObj, "quality_reasons")); color: colorText }
                        Label { text: "fi_valid: " + safeText(getField(runtimeObj, "fi_valid")); color: colorText }
                        Label { text: "control_state_reason: " + safeText(getField(runtimeObj, "control_state_reason")); color: colorText }
                        Label { text: "report_path: " + safeText(getField(sessionObj, "report_path")); color: colorText }
                        Label { text: "gameHudJson: " + safeText(guiBridge ? guiBridge.gameHudJson : "n/a"); color: colorMuted }
                        Label { text: "device_connected: " + safeText(getField(runtimeObj, "device_connected")); color: colorText }
                        Label { text: "attention_age_ms: " + safeText(getField(runtimeObj, "attention_age_ms")); color: colorText }
                        Label { text: "attention_last_update_ms: " + safeText(getField(runtimeObj, "attention_last_update_ms")); color: colorText }
                        Label { text: "gyro_x: " + safeText(getField(runtimeObj, "gyro_x")); color: colorText }
                        Label { text: "gyro_y: " + safeText(getField(runtimeObj, "gyro_y")); color: colorText }
                        Label { text: "gyro_z: " + safeText(getField(runtimeObj, "gyro_z")); color: colorText }
                        Label { text: "gyro_age_ms: " + safeText(getField(runtimeObj, "gyro_age_ms")); color: colorText }
                        Label { text: "gyro_last_update_ms: " + safeText(getField(runtimeObj, "gyro_last_update_ms")); color: colorText }
                        Label { text: "session_type: " + safeText(getField(sessionObj, "session_type")); color: colorText }
                        Label { text: "session_id: " + safeText(getField(sessionObj, "session_id")); color: colorText }
                        Label { text: "current_session_id: " + safeText(getField(controlStateObj, "current_session_id")); color: colorText }
                        Label { text: "session_elapsed_ms: " + safeText(getField(controlStateObj, "session_elapsed_ms")); color: colorText }
                        Label { text: "behavior_sample_count: " + safeText(getField(sessionObj, "behavior_sample_count")); color: colorText }
                        Label { text: "Runtime Snapshot"; color: colorMuted }

                    }
                }
            }

            Rectangle {
                width: 280; height: parent.height; color: colorPanel; radius: 8
                Column { anchors.fill: parent; anchors.margins: 8; spacing: 6
                    Label { text: "Feedback"; color: colorText; font.bold: true }
                    Label { text: "last_command: " + safeText(getField(controlStateObj, "last_command")); color: colorText }
                    Label { text: "last_command_result: " + safeText(getField(controlStateObj, "last_command_result")); color: colorText }
                    Label { text: "last_command_error: " + safeText(getField(controlStateObj, "last_command_error")); color: colorText }
                    Label { text: "command_count: " + safeText(getField(controlStateObj, "command_count")); color: colorText }
                    Label { text: "warning_flags: " + safeText(getField(runtimeObj, "warning_flags")); color: colorText }
                    Label { text: "error_flags: " + safeText(getField(runtimeObj, "error_flags")); color: colorText }
                    Label { text: "guiBridge.appState / guiBridge.runtimeSnapshot / guiBridge.sessionState / guiBridge.gameHudJson / guiBridge.controlManifestJson / guiBridge.controlStateJson"; color: colorMuted; wrapMode: Text.WordWrap }
                    Label { text: "action path: guiBridge.invokeAction"; color: colorMuted }
                    Label { text: "pageCommandManifestJson schema: " + safeText(getField(pageCommandManifestObj, "schema_version")); color: colorMuted }
                }
            }
        }
    }
}

// tokens: Runtime Snapshot Connection Attention Gyroscope Session Game HUD
