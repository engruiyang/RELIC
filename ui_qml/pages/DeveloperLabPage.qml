import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root

    property var guiBridge: null
    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var renderResourcesObj: ({})
    property var controlStateObj: ({})
    property string commandSummary: ""
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""
    property string selectedCliReference: ""
    property string fiGridActionRaw: ""
    property string fiGridStatus: "idle"
    property string fiGridMessage: "No FI grid action has been started."
    property string fiGridOutConfig: "n/a"
    property string fiGridReportPath: "n/a"
    property string fiGridElapsedMs: "n/a"
    property string fiGridInputCount: "n/a"
    property string fiGridLabelsCount: "n/a"

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    function safeJsonParse(raw) {
        try {
            return JSON.parse(raw || "{}")
        } catch (e) {
            return {"status": "parse_error", "message": String(e), "raw": raw || ""}
        }
    }

    function fiGridPayload() {
        return {
            "input_glob": fiGridInputField.text,
            "labels_glob": fiGridLabelsField.text,
            "base_config": fiGridConfigField.text,
            "out_dir": fiGridOutDirField.text,
            "stage_limit": parseInt(fiGridStageLimitField.text || "50"),
            "top_k": parseInt(fiGridTopKField.text || "10"),
            "timeout_sec": parseInt(fiGridTimeoutField.text || "60")
        }
    }

    function invokeFiGridAction(actionId) {
        selectedCommandId = actionId
        selectedStatus = "clicked"
        selectedExecutionMode = "native"
        selectedNativeActionId = actionId
        selectedCliReference = "GUI native wrapper for ui_cli.grid_calibrate_task6b"

        var raw = "{}"
        if (root.guiBridge) {
            raw = root.guiBridge.invokeAction(actionId, JSON.stringify(fiGridPayload()))
        } else {
            raw = JSON.stringify({"status": "missing_bridge", "message": "guiBridge unavailable"})
        }

        fiGridActionRaw = raw
        var obj = safeJsonParse(raw)
        var detail = obj.detail || obj.result || obj
        fiGridStatus = s(obj.status || detail.status)
        fiGridMessage = s(obj.message || detail.message)
        fiGridOutConfig = s(obj.out_config || detail.out_config)
        fiGridReportPath = s(obj.report_path || detail.report_path)
        fiGridElapsedMs = s(obj.elapsed_ms || detail.elapsed_ms)
        fiGridInputCount = s(obj.input_count || detail.input_count)
        fiGridLabelsCount = s(obj.labels_count || detail.labels_count)
        selectedStatus = fiGridStatus
    }

    function stateValue(key, fallbackValue) {
        var obj = root.controlStateObj || ({})
        if (obj[key] === undefined || obj[key] === null || obj[key] === "") {
            return fallbackValue
        }
        return obj[key]
    }

    function configValue(key, fallbackValue) {
        var obj = root.controlStateObj || ({})
        var cfg = obj.task6b_config_summary || obj.task6b_config || ({})
        if (cfg[key] === undefined || cfg[key] === null || cfg[key] === "") {
            return fallbackValue
        }
        return cfg[key]
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: (root.designThemeObj.colors && root.designThemeObj.colors.background) ? root.designThemeObj.colors.background : "#0B1420"
    }

    Flickable {
        id: developerLabScroll
        anchors.fill: parent
        clip: true
        contentWidth: width
        contentHeight: developerLabContent.implicitHeight + 20
        boundsBehavior: Flickable.StopAtBounds

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }

        Column {
            id: developerLabContent
            width: developerLabScroll.width
            spacing: 12

            PageHeader {
                renderResourcesObj: root.renderResourcesObj
                designThemeObj: root.designThemeObj
                componentStyleObj: root.componentStyleObj
                headerStyleObj: root.componentStyleObj.header || ({})
                titleText: "Developer Lab"
                subtitleText: "Task6B / FI engineering console · focused controls only"
            }

            Rectangle {
                id: devlabRoleCard
                objectName: "devlab_role_card"
                width: parent.width
                height: 104
                radius: 18
                color: "#0E1A28"
                border.color: "#31526A"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 5

                    Text {
                        text: "Developer Lab is now an algorithm experiment bench."
                        color: "#EAF6FF"
                        font.pixelSize: 17
                        font.bold: true
                    }
                    Text {
                        width: parent.width
                        text: "Legacy preview cards and copy-only debug button walls were removed from this page. Use this page for FI/SQI inspection and controlled Task6B grid experiments."
                        color: "#B8D4E8"
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }
                    Text {
                        width: parent.width
                        text: "The existing grid calibration algorithm is only invoked through safe native wrappers; its calculation file and result semantics are not edited here."
                        color: "#7FE7FF"
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }
                }
            }

            Row {
                width: parent.width
                spacing: 12

                Rectangle {
                    id: runtimeDataPanel
                    objectName: "devlab_runtime_data_panel"
                    width: Math.floor(parent.width * 0.50) - 6
                    height: 210
                    radius: 18
                    color: "#101C2A"
                    border.color: "#294A63"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 7

                        Text {
                            text: "Runtime Data Panel"
                            color: "#EAF6FF"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        Text { text: "current_user_id: " + s(stateValue("current_user_id", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "quality_state: " + s(stateValue("quality_state", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "control_state: " + s(stateValue("control_state", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "sqi: " + s(stateValue("sqi", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "fi_smoothed: " + s(stateValue("fi_smoothed", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "session_active: " + s(stateValue("session_active", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                    }
                }

                Rectangle {
                    id: task6bConfigPanel
                    objectName: "devlab_task6b_config_panel"
                    width: Math.floor(parent.width * 0.50) - 6
                    height: 210
                    radius: 18
                    color: "#101C2A"
                    border.color: "#294A63"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 7

                        Text {
                            text: "Task6B Config Snapshot"
                            color: "#EAF6FF"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        Text { text: "base_config: config/task6b.yaml"; color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "sqi_ok_threshold: " + s(configValue("sqi_ok_threshold", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "sqi_invalid_threshold: " + s(configValue("sqi_invalid_threshold", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "fi_ema_alpha: " + s(configValue("fi_ema_alpha", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "attention_low_fallback: " + s(configValue("attention_low_fallback", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                        Text { text: "attention_high_fallback: " + s(configValue("attention_high_fallback", "n/a")); color: "#CFE8F7"; font.pixelSize: 12 }
                    }
                }
            }

            Rectangle {
                id: fiGridPanel
                objectName: "devlab_fi_grid_panel"
                width: parent.width
                height: 350
                radius: 20
                color: "#0E1A28"
                border.color: "#2E5B72"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 10

                    Text {
                        text: "FI Grid Search Lab (Experimental)"
                        color: "#EAF6FF"
                        font.pixelSize: 18
                        font.bold: true
                    }
                    Text {
                        width: parent.width
                        text: "Use Dry Run Plan before Run Small Grid. Full staged search is intentionally not exposed from GUI. Outputs are written under reports/devlab/."
                        color: "#9FB6C8"
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }

                    Row {
                        width: parent.width
                        spacing: 8

                        Column {
                            width: Math.floor(parent.width * 0.50) - 6
                            spacing: 4
                            Text { text: "Input JSONL glob"; color: "#CFE8F7"; font.pixelSize: 12 }
                            TextField {
                                id: fiGridInputField
                                width: parent.width
                                text: "logs/task6b/*.jsonl"
                                placeholderText: "logs/task6b/*.jsonl"
                            }
                        }
                        Column {
                            width: Math.floor(parent.width * 0.50) - 6
                            spacing: 4
                            Text { text: "Labels CSV glob"; color: "#CFE8F7"; font.pixelSize: 12 }
                            TextField {
                                id: fiGridLabelsField
                                width: parent.width
                                text: "labels/task6b/*.frames.csv"
                                placeholderText: "labels/task6b/*.frames.csv"
                            }
                        }
                    }

                    Row {
                        width: parent.width
                        spacing: 8

                        Column {
                            width: Math.floor(parent.width * 0.38) - 6
                            spacing: 4
                            Text { text: "Base config"; color: "#CFE8F7"; font.pixelSize: 12 }
                            TextField {
                                id: fiGridConfigField
                                width: parent.width
                                text: "config/task6b.yaml"
                            }
                        }
                        Column {
                            width: Math.floor(parent.width * 0.30) - 6
                            spacing: 4
                            Text { text: "Output directory"; color: "#CFE8F7"; font.pixelSize: 12 }
                            TextField {
                                id: fiGridOutDirField
                                width: parent.width
                                text: "reports/devlab"
                            }
                        }
                        Column {
                            width: Math.floor(parent.width * 0.16) - 6
                            spacing: 4
                            Text { text: "Stage limit"; color: "#CFE8F7"; font.pixelSize: 12 }
                            TextField {
                                id: fiGridStageLimitField
                                width: parent.width
                                text: "50"
                            }
                        }
                        Column {
                            width: Math.floor(parent.width * 0.16) - 6
                            spacing: 4
                            Text { text: "Top K / timeout"; color: "#CFE8F7"; font.pixelSize: 12 }
                            Row {
                                width: parent.width
                                spacing: 4
                                TextField {
                                    id: fiGridTopKField
                                    width: Math.floor(parent.width * 0.45)
                                    text: "10"
                                }
                                TextField {
                                    id: fiGridTimeoutField
                                    width: Math.floor(parent.width * 0.50)
                                    text: "60"
                                }
                            }
                        }
                    }

                    Row {
                        spacing: 8

                        DesignButton {
                            buttonStyleObj: root.componentStyleObj.button || ({})
                            themeObj: root.designThemeObj
                            renderResourcesObj: root.renderResourcesObj
                            text: "Dry Run Plan"
                            onClicked: invokeFiGridAction("devlab.fi_grid_plan")
                        }
                        DesignButton {
                            buttonStyleObj: root.componentStyleObj.button || ({})
                            themeObj: root.designThemeObj
                            renderResourcesObj: root.renderResourcesObj
                            text: "Run Small Grid"
                            onClicked: invokeFiGridAction("devlab.fi_grid_small_run")
                        }
                    }
                }
            }

            Rectangle {
                id: fiGridResultPanel
                objectName: "devlab_fi_grid_result_panel"
                width: parent.width
                height: 178
                radius: 18
                color: "#0B1522"
                border.color: "#2A455D"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 5

                    Text {
                        text: "FI Grid Result"
                        color: "#EAF6FF"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    Text { text: "status: " + fiGridStatus + "    message: " + fiGridMessage; color: "#CFE8F7"; font.pixelSize: 12; wrapMode: Text.WrapAnywhere; width: parent.width }
                    Text { text: "input_count: " + fiGridInputCount + "    labels_count: " + fiGridLabelsCount; color: "#CFE8F7"; font.pixelSize: 12; wrapMode: Text.WrapAnywhere; width: parent.width }
                    Text { text: "out_config: " + fiGridOutConfig; color: "#9FB6C8"; font.pixelSize: 12; wrapMode: Text.WrapAnywhere; width: parent.width }
                    Text { text: "report_path: " + fiGridReportPath; color: "#9FB6C8"; font.pixelSize: 12; wrapMode: Text.WrapAnywhere; width: parent.width }
                    Text { text: "elapsed_ms: " + fiGridElapsedMs; color: "#7FA4B8"; font.pixelSize: 12; wrapMode: Text.WrapAnywhere; width: parent.width }
                }
            }

            Rectangle {
                id: devlabCommandSummaryPanel
                objectName: "devlab_command_summary_panel"
                width: parent.width
                height: 112
                radius: 18
                color: "#101C2A"
                border.color: "#28465E"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 5

                    Text {
                        text: "Page Commands"
                        color: "#EAF6FF"
                        font.pixelSize: 15
                        font.bold: true
                    }
                    Text {
                        width: parent.width
                        text: commandSummary
                        color: "#9FB6C8"
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }
                }
            }

            PageFeedbackPanel {
                renderResourcesObj: root.renderResourcesObj
                designThemeObj: root.designThemeObj
                componentStyleObj: root.componentStyleObj
                feedbackStyleObj: root.componentStyleObj.feedback_panel || ({})
                pageId: "developer_lab"
                selectedCommandId: root.selectedCommandId
                selectedStatus: root.selectedStatus
                selectedExecutionMode: root.selectedExecutionMode
                selectedNativeActionId: root.selectedNativeActionId
                lastCommand: s(controlStateObj.last_command)
                lastResult: s(controlStateObj.last_command_result)
                lastError: s(controlStateObj.last_command_error)
            }
        }
    }
}

// Page Feedback
// Developer Lab focused console tokens: Runtime Data Panel Task6B Config Snapshot FI Grid Search Lab (Experimental) FI Grid Result Page Commands Page Feedback
// Removed legacy preview tokens intentionally: no copy-only button wall, no TASK26 preview cards on this page.
