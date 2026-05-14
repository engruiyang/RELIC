import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 640
    height: 760
    title: "RELIC Minimal GUI"

    property var appStateObj: guiBridge ? JSON.parse(guiBridge.appState) : ({})
    property var runtimeObj: guiBridge ? JSON.parse(guiBridge.runtimeSnapshot) : ({})
    property var sessionObj: guiBridge ? JSON.parse(guiBridge.sessionState) : ({})

    Connections {
        target: guiBridge ? guiBridge : null
        function onStateChanged() {
            appStateObj = guiBridge ? JSON.parse(guiBridge.appState) : ({})
            runtimeObj = guiBridge ? JSON.parse(guiBridge.runtimeSnapshot) : ({})
            sessionObj = guiBridge ? JSON.parse(guiBridge.sessionState) : ({})
        }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 6

        Text { text: "Mode: " + (appStateObj.source && appStateObj.source.indexOf("core") === 0 ? "core" : "mock") }
        Text { text: "Source: " + (appStateObj.source || "") }
        Text { text: "App State: " + (appStateObj.state || "") }
        Text { text: "User ID: " + (appStateObj.current_user_id || "") }
        Text { text: "User Name: " + (appStateObj.current_user_name || "") }
        Text { text: "Device Connected: " + (appStateObj.device_connected !== undefined ? appStateObj.device_connected : "") }
        Text { text: "Calibration Status: " + (appStateObj.calibration_status || "") }
        Text { text: "FI: " + (runtimeObj.fi !== undefined ? runtimeObj.fi : "") }
        Text { text: "SQI: " + (runtimeObj.sqi !== undefined ? runtimeObj.sqi : "") }
        Text { text: "Attention: " + (runtimeObj.attention !== undefined ? runtimeObj.attention : "") }
        Text { text: "Attention Age: " + (runtimeObj.attention_age_ms !== undefined ? runtimeObj.attention_age_ms : "") }
        Text { text: "Gyro Age: " + (runtimeObj.gyro_age_ms !== undefined ? runtimeObj.gyro_age_ms : "") }
        Text { text: "Control State: " + (runtimeObj.control_state || "") }
        Text { text: "Session ID: " + (sessionObj.session_id || "") }
        Text { text: "Score: " + (sessionObj.score !== undefined ? sessionObj.score : "") }
        Text { text: "Warning Count: " + (sessionObj.warning_count !== undefined ? sessionObj.warning_count : "") }
        Text { text: "Error Count: " + (sessionObj.error_count !== undefined ? sessionObj.error_count : "") }
        Text { text: "Log Path: " + (sessionObj.log_path || "") }
        Text { text: "Report Path: " + (sessionObj.report_path || "") }

        Button { text: "Load Demo User"; onClicked: guiBridge.sendCommand("load_demo_user", "{}") }
        Button { text: "Start Mock Session"; onClicked: guiBridge.sendCommand("start_mock_session", "{}") }
        Button { text: "End Session"; onClicked: guiBridge.sendCommand("end_session", "{}") }
        Button { text: "Refresh Snapshot"; onClicked: guiBridge.refresh() }
        Button {
            text: "Send Test Click"
            onClicked: guiBridge.sendEvent("target_click", JSON.stringify({
                "game_id": "fake_game",
                "target_id": "mock_target_0",
                "target_index": 0,
                "x_norm": 0.5,
                "y_norm": 0.5,
                "button": "left"
            }))
        }

        Rectangle { width: parent.width; height: 1; color: "#888" }
        Text { text: "Command Count: " + (guiBridge ? guiBridge.commandCount : 0) }
        Text { text: "Last Command: " + ((guiBridge && guiBridge.lastCommand !== "") ? guiBridge.lastCommand : "<none>") }
        Text { text: "Last Command Result: " + ((guiBridge && guiBridge.lastCommandResult !== "") ? guiBridge.lastCommandResult : "<none>") }
        Text { text: "Event Count: " + (guiBridge ? guiBridge.eventCount : 0) }
        Text { text: "Last Event: " + ((guiBridge && guiBridge.lastEvent !== "") ? guiBridge.lastEvent : "<none>") }
        Text { text: "Last Event Result: " + ((guiBridge && guiBridge.lastEventResult !== "") ? guiBridge.lastEventResult : "<none>") }
    }
}
