import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 1000
    height: 700
    title: "RELIC Core"

    property var appStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameHudObj: ({})

    function safeParseJson(jsonText) {
        try {
            return JSON.parse(jsonText || "{}")
        } catch (e) {
            return ({})
        }
    }

    function na(value) {
        return value === undefined || value === null || value === "" ? "n/a" : value
    }

    function pullState() {
        if (!guiBridge) {
            appStateObj = ({})
            runtimeObj = ({})
            sessionObj = ({})
            gameHudObj = ({})
            return
        }
        appStateObj = safeParseJson(guiBridge.appState)
        runtimeObj = safeParseJson(guiBridge.runtimeSnapshot)
        sessionObj = safeParseJson(guiBridge.sessionState)
        gameHudObj = safeParseJson(guiBridge.gameHudJson)
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

        Label { text: "RELIC Core / TraceLock Control Shell"; font.pixelSize: 24; font.bold: true }
        Label { text: "QML smoke shell loaded"; font.pixelSize: 16 }

        GroupBox {
            width: parent.width
            title: "Protocol Select"
            Column {
                spacing: 4
                Label { text: "mode: " + na(appStateObj.mode) }
                Label { text: "source: " + na(appStateObj.source) }
                Label { text: "game_id: " + na(appStateObj.current_game_id || appStateObj.game_id) }
                Label { text: "currentSessionType: " + na(sessionObj.currentSessionType || sessionObj.session_type) }
            }
        }

        GroupBox {
            width: parent.width
            title: "TraceLock Training"
            Column {
                spacing: 4
                Label { text: "Trace Score: " + na(gameHudObj.score) }
                Label { text: "Sync Chain / Combo: " + na(gameHudObj.combo) }
                Label { text: "Max Combo: " + na(gameHudObj.max_combo) }
                Label { text: "Multiplier: " + na(gameHudObj.score_multiplier) }
                Label { text: "Load Tier / Level: " + na(gameHudObj.load_tier) + " / " + na(gameHudObj.level) }
                Label { text: "Movement Type: " + na(gameHudObj.movement_type) }
                Label { text: "Lock Window: " + na(gameHudObj.target_time_left_ms) }
                Label { text: "Trace Retention: " + na(gameHudObj.accuracy) }
                Label { text: "Trace Drop: " + na(gameHudObj.omission) }
                Label { text: "False Action: " + na(gameHudObj.false_action) }
                Label { text: "RT Stability: " + na(gameHudObj.rt_stability) }
            }
        }

        GroupBox {
            width: parent.width
            title: "Training Controls"
            Column {
                spacing: 6
                Row {
                    spacing: 8
                    Button { text: "Start Training Session"; onClicked: { if (guiBridge) { guiBridge.sendCommand("start_training_session", "{}") } } }
                    Button { text: "End Training Session"; onClicked: { if (guiBridge) { guiBridge.sendCommand("end_training_session", "{}") } } }
                    Button {
                        text: "Refresh Snapshot"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("refresh_snapshot", "{}")
                            }
                            pullState()
                        }
                    }
                }
                Label { text: "session_id: " + na(sessionObj.session_id) }
                Label { text: "latest_report_path: " + na(sessionObj.latest_report_path || sessionObj.report_path) }
                Label { text: "training_status: " + na(sessionObj.training_status) }
            }
        }

        GroupBox {
            width: parent.width
            title: "Debug Panel"
            Column {
                spacing: 6
                Row {
                    spacing: 8
                    Button { text: "Start Mock Session (Debug)"; onClicked: { if (guiBridge) { guiBridge.sendCommand("start_mock_session", "{}") } } }
                    Button { text: "End Session"; onClicked: { if (guiBridge) { guiBridge.sendCommand("end_session", "{}") } } }
                }
                Row {
                    spacing: 8
                    Button { text: "Force L1"; onClicked: { if (guiBridge) { guiBridge.sendCommand("set_debug_difficulty", "{\"level\":1}") } } }
                    Button { text: "Force L2"; onClicked: { if (guiBridge) { guiBridge.sendCommand("set_debug_difficulty", "{\"level\":2}") } } }
                    Button { text: "Force L3"; onClicked: { if (guiBridge) { guiBridge.sendCommand("set_debug_difficulty", "{\"level\":3}") } } }
                    Button { text: "Force L4"; onClicked: { if (guiBridge) { guiBridge.sendCommand("set_debug_difficulty", "{\"level\":4}") } } }
                    Button { text: "Force L5"; onClicked: { if (guiBridge) { guiBridge.sendCommand("set_debug_difficulty", "{\"level\":5}") } } }
                    Button { text: "Auto DDA"; onClicked: { if (guiBridge) { guiBridge.sendCommand("set_debug_difficulty", "{\"level\":null}") } } }
                }
            }
        }

        GroupBox {
            width: parent.width
            title: "Link Diagnostics"
            Label { text: "latest_report_path: " + na(sessionObj.latest_report_path || sessionObj.report_path) }
        }

        GroupBox {
            width: parent.width
            title: "NAC / Live Status"
            Column {
                spacing: 4
                Label { text: "connection_status: " + na(runtimeObj.connection_status) }
                Label { text: "stream_alive: " + na(runtimeObj.stream_alive) }
                Label { text: "attention: " + na(runtimeObj.attention) }
                Label { text: "attention_fresh: " + na(runtimeObj.attention_fresh) }
                Label { text: "attention_age_ms: " + na(runtimeObj.attention_age_ms) }
                Label { text: "gyro_x: " + na(runtimeObj.gyro_x) }
                Label { text: "gyro_y: " + na(runtimeObj.gyro_y) }
                Label { text: "gyro_z: " + na(runtimeObj.gyro_z) }
                Label { text: "gyro_fresh: " + na(runtimeObj.gyro_fresh) }
                Label { text: "gyro_age_ms: " + na(runtimeObj.gyro_age_ms) }
                Label { text: "warning_flags: " + na(JSON.stringify(runtimeObj.warning_flags || runtimeObj.current_warning_flags)) }
                Label { text: "error_flags: " + na(JSON.stringify(runtimeObj.error_flags)) }
            }
        }
    }
}
