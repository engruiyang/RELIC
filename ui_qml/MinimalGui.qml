import QtQuick
import QtQuick.Controls
import "components"

ApplicationWindow {
    visible: true
    width: 640
    height: 760
    title: "RELIC Minimal GUI"

    property var appStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameViewObj: ({})
    property var resourceBundleObj: ({})

    function safeParseJson(jsonText) {
        try {
            return JSON.parse(jsonText || "{}")
        } catch (e) {
            return ({ "error": "json_parse_failed" })
        }
    }

    Connections {
        target: guiBridge ? guiBridge : null
        function onStateChanged() {
            appStateObj = guiBridge ? safeParseJson(guiBridge.appState) : ({})
            runtimeObj = guiBridge ? safeParseJson(guiBridge.runtimeSnapshot) : ({})
            sessionObj = guiBridge ? safeParseJson(guiBridge.sessionState) : ({})
            gameViewObj = guiBridge ? safeParseJson(guiBridge.gameViewJson) : ({})
            resourceBundleObj = guiBridge ? safeParseJson(guiBridge.renderResourcesJson) : ({})
        }
    }

    Component.onCompleted: {
        appStateObj = guiBridge ? safeParseJson(guiBridge.appState) : ({})
        runtimeObj = guiBridge ? safeParseJson(guiBridge.runtimeSnapshot) : ({})
        sessionObj = guiBridge ? safeParseJson(guiBridge.sessionState) : ({})
        gameViewObj = guiBridge ? safeParseJson(guiBridge.gameViewJson) : ({})
        resourceBundleObj = guiBridge ? safeParseJson(guiBridge.renderResourcesJson) : ({})
    }

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 6

        Text { text: "Mode: " + (appStateObj.source === "live_readonly" ? "live-readonly" : (appStateObj.source && appStateObj.source.indexOf("core") === 0 ? "core" : "mock")) }
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
            onClicked: guiBridge.sendEvent("pointer_click", JSON.stringify({
                "game_id": "fake_game",
                "x_norm": 0.5,
                "y_norm": 0.5,
                "button": "left"
            }))
        }
        GameCanvas {
            width: parent.width
            height: 220
            gameView: gameViewObj
            guiBridgeRef: guiBridge
            fallbackGameId: "fake_game"
        }

        Rectangle { width: parent.width; height: 1; color: "#888" }
        Text { text: "Click x_norm: " + ((guiBridge && guiBridge.lastPointerX !== "") ? guiBridge.lastPointerX : "<none>") }
        Text { text: "Click y_norm: " + ((guiBridge && guiBridge.lastPointerY !== "") ? guiBridge.lastPointerY : "<none>") }
        Text { text: "Last Hit: " + ((guiBridge && guiBridge.lastHitState !== "") ? guiBridge.lastHitState : "<none>") }
        Text { text: "Command Count: " + (guiBridge ? guiBridge.commandCount : 0) }
        Text { text: "Last Command: " + ((guiBridge && guiBridge.lastCommand !== "") ? guiBridge.lastCommand : "<none>") }
        Text { text: "Last Command Result: " + ((guiBridge && guiBridge.lastCommandResult !== "") ? guiBridge.lastCommandResult : "<none>") }
        Text { text: "Event Count: " + (guiBridge ? guiBridge.eventCount : 0) }
        Text { text: "Last Event: " + ((guiBridge && guiBridge.lastEvent !== "") ? guiBridge.lastEvent : "<none>") }
        Text { text: "Last Event Result: " + ((guiBridge && guiBridge.lastEventResult !== "") ? guiBridge.lastEventResult : "<none>") }
        Text { text: "Game Event Count: " + (guiBridge ? guiBridge.gameEventCount : 0) }
        Text { text: "Last Game Event: " + ((guiBridge && guiBridge.lastGameEvent !== "") ? guiBridge.lastGameEvent : "<none>") }
        Text { text: "Last Game Event Type: " + ((guiBridge && guiBridge.lastGameEventType !== "") ? guiBridge.lastGameEventType : "<none>") }
        Text { text: "Last Game Action: " + ((guiBridge && guiBridge.lastGameActionName !== "") ? guiBridge.lastGameActionName : "<none>") }
        Text { text: "Last Game Target Index: " + ((guiBridge && guiBridge.lastGameTargetIndex !== "") ? guiBridge.lastGameTargetIndex : "<none>") }
        Text { text: "Game View Score: " + ((guiBridge && guiBridge.gameViewScore !== "") ? guiBridge.gameViewScore : "<none>") }
        Text { text: "Game View Combo: " + ((guiBridge && guiBridge.gameViewCombo !== "") ? guiBridge.gameViewCombo : "<none>") }
        Text { text: "Game View Entity Count: " + ((guiBridge && guiBridge.gameViewEntityCount !== "") ? guiBridge.gameViewEntityCount : "<none>") }
        Text { text: "Game View Visual Event Count: " + ((guiBridge && guiBridge.gameViewVisualEventCount !== "") ? guiBridge.gameViewVisualEventCount : "<none>") }
        Text { text: "Platform Message Count: " + (guiBridge ? guiBridge.platformMessageCount : 0) }
        Text { text: "Last Platform Message: " + ((guiBridge && guiBridge.lastPlatformMessage !== "") ? guiBridge.lastPlatformMessage : "<none>") }
        Text { text: "Last Platform Index: " + ((guiBridge && guiBridge.lastPlatformIndex !== "") ? guiBridge.lastPlatformIndex : "<none>") }
        Text { text: "Last Platform Action: " + ((guiBridge && guiBridge.lastPlatformAction !== "") ? guiBridge.lastPlatformAction : "<none>") }
        Text { text: "Last Platform Result: " + ((guiBridge && guiBridge.lastPlatformResult !== "") ? guiBridge.lastPlatformResult : "<none>") }


        Rectangle { width: parent.width; height: 1; color: "#888" }
        Text { text: "Resource Bundle" }
        Text { text: "Theme ID: " + (resourceBundleObj.theme_id || "") }
        Text { text: "Layout ID: " + (resourceBundleObj.layout_id || "") }
        Text { text: "Game ID: " + (resourceBundleObj.game_id || "") }
        Text { text: "Asset Count: " + (resourceBundleObj.assets ? Object.keys(resourceBundleObj.assets).length : 0) }
        Text { text: "Style Count: " + (resourceBundleObj.styles ? Object.keys(resourceBundleObj.styles).length : 0) }
        Text { text: "Layout Region Count: " + (resourceBundleObj.layout_regions ? Object.keys(resourceBundleObj.layout_regions).length : 0) }
        Text { text: "Missing Assets: " + (resourceBundleObj.missing_assets ? resourceBundleObj.missing_assets.length : 0) }
        Text { text: "Missing Styles: " + (resourceBundleObj.missing_styles ? resourceBundleObj.missing_styles.length : 0) }
        Text { text: "Missing Regions: " + (resourceBundleObj.missing_regions ? resourceBundleObj.missing_regions.length : 0) }
        Text { text: "Resource Error: " + (resourceBundleObj.error || "") }

        Rectangle { width: parent.width; height: 1; color: "#888" }
        Text { text: "Live Stream" }
        Text { text: "Connection Status: " + (runtimeObj.connection_status !== undefined ? runtimeObj.connection_status : "-") }
        Text { text: "Stream Alive: " + (runtimeObj.stream_alive !== undefined ? runtimeObj.stream_alive : "-") }
        Text { text: "Raw Messages: " + (runtimeObj.raw_message_count !== undefined ? runtimeObj.raw_message_count : "-") }
        Text { text: "Attention Count: " + (runtimeObj.decoded_attention_count !== undefined ? runtimeObj.decoded_attention_count : "-") }
        Text { text: "Gyro Count: " + (runtimeObj.decoded_gyro_count !== undefined ? runtimeObj.decoded_gyro_count : "-") }
        Text { text: "Attention: " + (runtimeObj.attention !== undefined ? runtimeObj.attention : "-") }
        Text { text: "Attention Age: " + (runtimeObj.attention_age_ms !== undefined ? runtimeObj.attention_age_ms : "-") }
        Text { text: "Attention Fresh: " + (runtimeObj.attention_fresh !== undefined ? runtimeObj.attention_fresh : "-") }
        Text { text: "Gyro X/Y/Z: " + (runtimeObj.gyro_x !== undefined ? runtimeObj.gyro_x : "-") + "/" + (runtimeObj.gyro_y !== undefined ? runtimeObj.gyro_y : "-") + "/" + (runtimeObj.gyro_z !== undefined ? runtimeObj.gyro_z : "-") }
        Text { text: "Gyro Age: " + (runtimeObj.gyro_age_ms !== undefined ? runtimeObj.gyro_age_ms : "-") }
        Text { text: "Gyro Fresh: " + (runtimeObj.gyro_fresh !== undefined ? runtimeObj.gyro_fresh : "-") }
        Text { text: "Current Warning Flags: " + (runtimeObj.current_warning_flags !== undefined ? JSON.stringify(runtimeObj.current_warning_flags) : "-") }
        Text { text: "Historical Warning Flags: " + (runtimeObj.historical_warning_flags !== undefined ? JSON.stringify(runtimeObj.historical_warning_flags) : "-") }
        Text { text: "Error Flags: " + (runtimeObj.error_flags !== undefined ? JSON.stringify(runtimeObj.error_flags) : "-") }
        Text { text: "Error Message: " + (runtimeObj.error_message !== undefined && runtimeObj.error_message !== null ? runtimeObj.error_message : "-") }
    }
}
