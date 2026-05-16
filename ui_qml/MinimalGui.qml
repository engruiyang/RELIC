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
            return
        }
        appStateObj = safeJsonParse(guiBridge.appState)
        runtimeObj = safeJsonParse(guiBridge.runtimeSnapshot)
        sessionObj = safeJsonParse(guiBridge.sessionState)
        gameHudObj = safeJsonParse(guiBridge.gameHudJson)
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

        Label { text: "RELIC Core / Live Bus Status"; font.pixelSize: 24; font.bold: true }
        Label { text: "QML smoke shell loaded"; font.pixelSize: 16 }

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
