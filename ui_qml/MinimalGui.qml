import QtQuick
import QtQuick.Controls
import "components"

ApplicationWindow {
    visible: true
    width: 980
    height: 820
    title: "RELIC Minimal GUI"

    property var appStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameViewObj: ({})
    property var gameHudObj: ({})

    function safeParseJson(jsonText) {
        try { return JSON.parse(jsonText || "{}") } catch (e) { return ({ "error": "json_parse_failed" }) }
    }

    function pullState() {
        appStateObj = guiBridge ? safeParseJson(guiBridge.appState) : ({})
        runtimeObj = guiBridge ? safeParseJson(guiBridge.runtimeSnapshot) : ({})
        sessionObj = guiBridge ? safeParseJson(guiBridge.sessionState) : ({})
        gameViewObj = guiBridge ? safeParseJson(guiBridge.gameViewJson) : ({})
        gameHudObj = guiBridge ? safeParseJson(guiBridge.gameHudJson) : ({})
    }

    Connections { target: guiBridge ? guiBridge : null; function onStateChanged() { pullState() } }
    Timer { interval: 100; running: true; repeat: true; onTriggered: { if (guiBridge) guiBridge.refresh() } }
    Component.onCompleted: pullState()

    ScrollView {
        anchors.fill: parent
        Column {
            width: parent.width
            spacing: 8
            padding: 12

            GroupBox {
                objectName: "protocolSelectPanel"
                width: parent.width
                title: "Protocol Select"
                Column {
                    spacing: 4
                    Text { text: "TraceLock Protocol" }
                    Text { text: "Data Trace Tracking Protocol" }
                    Text { text: "game_id=" + (appStateObj.current_game_id || "n/a") }
                    Button { text: "Enter Training"; onClicked: guiBridge.sendCommand("start_training_session", "{}") }
                }
            }

            GroupBox {
                objectName: "traceLockTrainingPanel"
                width: parent.width
                title: "TraceLock Training"
                Column {
                    spacing: 4
                    GameCanvas { width: parent.width - 20; height: 280; gameView: gameViewObj; guiBridgeRef: guiBridge; fallbackGameId: "fake_game" }
                    Text { text: "Trace Score: " + (gameHudObj.score !== undefined ? gameHudObj.score : "n/a") + " | Sync Chain / Combo: " + (gameHudObj.combo !== undefined ? gameHudObj.combo : "n/a") + " | Multiplier: " + (gameHudObj.score_multiplier !== undefined ? gameHudObj.score_multiplier : "n/a") }
                    Text { text: "Load Tier / Level: " + (gameHudObj.load_tier !== undefined ? gameHudObj.load_tier : "n/a") + "/" + (gameHudObj.level !== undefined ? gameHudObj.level : "n/a") + " | Movement Type: " + (gameHudObj.movement_type || "n/a") }
                    Text { text: "Lock Window / target_time_left_ms: " + (gameHudObj.target_time_left_ms !== undefined ? gameHudObj.target_time_left_ms : "n/a") }
                    Text { text: "Trace Retention / accuracy: " + (gameHudObj.accuracy !== undefined ? gameHudObj.accuracy : "n/a") + " | Trace Drop / omission: " + (gameHudObj.omission !== undefined ? gameHudObj.omission : "n/a") }
                    Text { text: "False Action: " + (gameHudObj.false_action !== undefined ? gameHudObj.false_action : "n/a") + " | RT Stability: " + (gameHudObj.rt_stability !== undefined ? gameHudObj.rt_stability : "n/a") }
                }
            }

            GroupBox {
                width: parent.width
                title: "Training Controls"
                Column {
                    spacing: 4
                    Row { spacing: 6
                        Button { text: "Start Training Session"; onClicked: guiBridge.sendCommand("start_training_session", "{}") }
                        Button { text: "End Training Session"; onClicked: guiBridge.sendCommand("end_training_session", "{}") }
                    }
                    Text { text: "session_type: " + (sessionObj.session_type || "n/a") }
                    Text { text: "session_id: " + (sessionObj.session_id || "n/a") }
                    Text { text: "report_path: " + (sessionObj.report_path || "n/a") }
                }
            }

            GroupBox {
                objectName: "debugControlPanel"
                width: parent.width
                title: "Debug Panel"
                Column {
                    spacing: 4
                    Row { spacing: 6
                        Button { text: "Start Mock Session (Debug)"; onClicked: guiBridge.sendCommand("start_mock_session", "{}") }
                        Button { text: "End Session"; onClicked: guiBridge.sendCommand("end_session", "{}") }
                        Button { text: "Refresh Snapshot"; onClicked: guiBridge.sendCommand("refresh_snapshot", "{}") }
                    }
                    Row { spacing: 4
                        Button { text: "Force L1"; onClicked: guiBridge.sendCommand("set_debug_difficulty", "{\"level\":1}") }
                        Button { text: "Force L2"; onClicked: guiBridge.sendCommand("set_debug_difficulty", "{\"level\":2}") }
                        Button { text: "Force L3"; onClicked: guiBridge.sendCommand("set_debug_difficulty", "{\"level\":3}") }
                        Button { text: "Force L4"; onClicked: guiBridge.sendCommand("set_debug_difficulty", "{\"level\":4}") }
                        Button { text: "Force L5"; onClicked: guiBridge.sendCommand("set_debug_difficulty", "{\"level\":5}") }
                        Button { text: "Auto DDA"; onClicked: guiBridge.sendCommand("set_debug_difficulty", "{\"level\":null}") }
                    }
                    Text { text: "last command: " + (guiBridge && guiBridge.lastCommand !== "" ? guiBridge.lastCommand : "n/a") }
                    Text { text: "last event: " + (guiBridge && guiBridge.lastEvent !== "" ? guiBridge.lastEvent : "n/a") }
                }
            }

            GroupBox {
                objectName: "linkDiagnosticsPanel"
                width: parent.width
                title: "Link Diagnostics"
                Column {
                    spacing: 4
                    Text { text: "latest report_path: " + (sessionObj.latest_report_path || sessionObj.report_path || "n/a") }
                    Text { text: "last session_id: " + (sessionObj.latest_session_id || sessionObj.session_id || "n/a") }
                    Text { text: "last training status: " + (sessionObj.training_status || "n/a") }
                    Button { text: "Open Last Report"; onClicked: guiBridge.sendCommand("open_last_report", "{}") }
                }
            }

            GroupBox {
                width: parent.width
                title: "NAC / Live Status"
                Column {
                    spacing: 4
                    Text { text: "connection_status: " + (runtimeObj.connection_status !== undefined ? runtimeObj.connection_status : "n/a") }
                    Text { text: "stream_alive: " + (runtimeObj.stream_alive !== undefined ? runtimeObj.stream_alive : "n/a") }
                    Text { text: "Focus Sync / attention_fresh: " + (runtimeObj.attention_fresh !== undefined ? runtimeObj.attention_fresh : "n/a") }
                    Text { text: "Gyro Link / gyro_fresh: " + (runtimeObj.gyro_fresh !== undefined ? runtimeObj.gyro_fresh : "n/a") }
                    Text { text: "warning_flags: " + (runtimeObj.current_warning_flags !== undefined ? JSON.stringify(runtimeObj.current_warning_flags) : "n/a") }
                    Text { text: "error_flags: " + (runtimeObj.error_flags !== undefined ? JSON.stringify(runtimeObj.error_flags) : "n/a") }
                }
            }
        }
    }
}
