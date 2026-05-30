import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var renderResourcesObj: ({})
    property bool task26DesktopPilotEnabled: true
    property bool task26LegacyFallbackVisible: false

    function task26DiagnosticsLayoutPayload() {
        var resources = root.renderResourcesObj || ({})
        return resources.task26_diagnostics_layout_payload || ({})
    }

    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameHudObj: ({})
    property string commandSummary: ""
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""

    signal invokeNative(string actionId)

    function pick(id, status, mode, nativeActionId) {
        selectedCommandId = id
        selectedStatus = status
        selectedExecutionMode = mode
        selectedNativeActionId = nativeActionId
        if (mode === "native" && nativeActionId !== "") {
            invokeNative(nativeActionId)
        }
    }

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: (root.designThemeObj.colors && root.designThemeObj.colors.background) ? root.designThemeObj.colors.background : "#F8FAFC"
    }


    Item {
        id: task26DiagnosticsDesktopPilotOverlay
        anchors.fill: parent
        anchors.margins: 6
        z: 100
        visible: root.task26DesktopPilotEnabled

        DesktopLayoutPreview {
            id: task26DiagnosticsDesktopLayoutPreview
            anchors.fill: parent
            layoutPayload: root.task26DiagnosticsLayoutPayload()
            previewTitle: "TASK26 Diagnostics Desktop Pilot"
            previewSubtitle: "Full-area card desktop pilot · legacy fallback: " + String(root.task26LegacyFallbackVisible)
            payloadStatusText: String((root.renderResourcesObj || ({})).task26_diagnostics_layout_status || "n/a")
            payloadSourceText: String((root.renderResourcesObj || ({})).task26_diagnostics_layout_source || "n/a")
        }
    }


    Column {
        anchors.fill: parent
        spacing: 4

        PageHeader {
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            headerStyleObj: root.componentStyleObj.header || ({})
            titleText: "Developer Diagnostics Console"
            subtitleText: "QML smoke shell loaded"
        }

        GroupBox {
            title: "Control Panel"
            Row {
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                    text: "Diagnostics Refresh"
                    onClicked: pick("diagnostics.refresh", "native_ready", "native", "diagnostics.refresh")
                }
            }
        }

        Label { text: "Live Input" }
        Label { text: "Quality / Focus (TASK6)" }

        GroupBox {
            title: "Connection / Runtime"
            Column {
                Label { text: "connection_status: " + s(runtimeObj.connection_status) }
                Label { text: "stream_alive: " + s(runtimeObj.stream_alive) }
                Label { text: "device_connected: " + s(runtimeObj.device_connected) }
            }
        }

        GroupBox {
            title: "Attention"
            Column {
                Label { text: "attention: " + s(runtimeObj.attention) }
                Label { text: "attention_fresh: " + s(runtimeObj.attention_fresh) }
                Label { text: "attention_age_ms: " + s(runtimeObj.attention_age_ms) }
                Label { text: "attention_last_update_ms: " + s(runtimeObj.attention_last_update_ms) }
            }
        }

        GroupBox {
            title: "Gyroscope"
            Column {
                Label { text: "gyro_x: " + s(runtimeObj.gyro_x) }
                Label { text: "gyro_y: " + s(runtimeObj.gyro_y) }
                Label { text: "gyro_z: " + s(runtimeObj.gyro_z) }
                Label { text: "gyro_fresh: " + s(runtimeObj.gyro_fresh) }
                Label { text: "gyro_age_ms: " + s(runtimeObj.gyro_age_ms) }
                Label { text: "gyro_last_update_ms: " + s(runtimeObj.gyro_last_update_ms) }
            }
        }

        GroupBox {
            title: "Session / Report"
            Column {
                Label { text: "session_type: " + s(sessionObj.session_type) }
                Label { text: "session_id: " + s(sessionObj.session_id) }
                Label { text: "session_active: " + s(controlStateObj.session_active) }
                Label { text: "current_session_id: " + s(controlStateObj.current_session_id) }
                Label { text: "session_elapsed_ms: " + s(controlStateObj.session_elapsed_ms) }
                Label { text: "latest_report_path: " + s(controlStateObj.latest_report_path) }
                Label { text: "report_path: " + s(sessionObj.report_path) }
                Label { text: "last_session_status: " + s(controlStateObj.last_session_status) }
            }
        }

        GroupBox {
            title: "Diagnostics"
            Column {
                Label { text: "warning_flags: " + s(runtimeObj.warning_flags) }
                Label { text: "error_flags: " + s(runtimeObj.error_flags) }
                Label { text: "last_command: " + s(controlStateObj.last_command) }
                Label { text: "last_command_result: " + s(controlStateObj.last_command_result) }
                Label { text: "last_command_error: " + s(controlStateObj.last_command_error) }
                Label { text: "command_count: " + s(controlStateObj.command_count) }
            }
        }

        GroupBox {
            title: "Quality / Focus"
            Column {
                Label { text: "sqi: " + s(runtimeObj.sqi) }
                Label { text: "quality_state: " + s(runtimeObj.quality_state) }
                Label { text: "quality_reasons: " + s(runtimeObj.quality_reasons) }
                Label { text: "fi_smoothed: " + s(runtimeObj.fi_smoothed) }
                Label { text: "fi_valid: " + s(runtimeObj.fi_valid) }
                Label { text: "control_state: " + s(runtimeObj.control_state) }
                Label { text: "control_state_reason: " + s(runtimeObj.control_state_reason) }
            }
        }

        GroupBox {
            title: "Profile / Calibration"
            Column {
                Label { text: "current_user_id: " + s(controlStateObj.current_user_id) }
                Label { text: "profile_status: " + s(controlStateObj.profile_status) }
                Label { text: "profile_loaded: " + s(controlStateObj.profile_loaded) }
                Label { text: "calibration_status: " + s(controlStateObj.calibration_status) }
                Label { text: "last_calibration_id: " + s(controlStateObj.last_calibration_id) }
                Label { text: "calibration_usable: " + s(controlStateObj.calibration_usable) }
            }
        }

        GroupBox {
            title: "Game HUD"
            Column {
                Label { text: "gameHudJson" }
                Label { text: "game_id: " + s(controlStateObj.current_game_id) }
                Label { text: "score: " + s(gameHudObj.score) }
                Label { text: "combo: " + s(gameHudObj.combo) }
                Label { text: "level: " + s(gameHudObj.level) }
                Label { text: "behavior_sample_count: " + s(sessionObj.behavior_sample_count) }
                Label { text: "score_update_count: " + s(gameHudObj.score_update_count) }
                Label { text: "feedback_hint: " + s(gameHudObj.feedback_hint) }
            }
        }

        GroupBox {
            title: "Page Commands"
            Label {
                text: commandSummary
                wrapMode: Text.WordWrap
            }
        }

        PageFeedbackPanel {
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            feedbackStyleObj: root.componentStyleObj.feedback_panel || ({})
            pageId: "diagnostics"
            selectedCommandId: parent.selectedCommandId
            selectedStatus: parent.selectedStatus
            selectedExecutionMode: parent.selectedExecutionMode
            selectedNativeActionId: parent.selectedNativeActionId
            lastCommand: s(controlStateObj.last_command)
            lastResult: s(controlStateObj.last_command_result)
            lastError: s(controlStateObj.last_command_error)
        }
    }
}

// Page Feedback
