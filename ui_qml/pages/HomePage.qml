import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root

    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var renderResourcesObj: ({})
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property string commandSummary: ""

    signal navigateTo(string pageId)
    signal invokeNative(string actionId)

    width: parent ? parent.width : 900
    height: parent ? parent.height : 600

    function safeText(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    function themeColor(key, fallbackValue) {
        var colors = root.designThemeObj.colors || ({})
        var value = colors[key]
        return (value === undefined || value === null || value === "") ? fallbackValue : value
    }

    function nextAction() {
        if (safeText(root.controlStateObj.current_user_id) === "n/a") {
            return "Next Action: Go User"
        }
        if (safeText(root.controlStateObj.calibration_usable) !== "true") {
            return "Next Action: Go Calibration"
        }
        return "Next Action: Go Training"
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: root.themeColor("background", "#F8FAFC")
    }

    Column {
        anchors.fill: parent
        spacing: 6

        PageHeader {
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            headerStyleObj: root.componentStyleObj.header || ({})
            titleText: "Home"
            subtitleText: "Professional overview page"
        }

        GroupBox {
            title: "State Summary"

            Column {
                Label {
                    text: "current_user_id: " + root.safeText(root.controlStateObj.current_user_id)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: "profile_status: " + root.safeText(root.controlStateObj.profile_status)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: "calibration_status: " + root.safeText(root.controlStateObj.calibration_status)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: "calibration_usable: " + root.safeText(root.controlStateObj.calibration_usable)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: "connection_status: " + root.safeText(root.runtimeObj.connection_status)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: "quality_state: " + root.safeText(root.runtimeObj.quality_state)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: "control_state: " + root.safeText(root.runtimeObj.control_state)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: "session_active: " + root.safeText(root.controlStateObj.session_active)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: "latest_report_path: " + root.safeText(root.controlStateObj.latest_report_path)
                    color: root.themeColor("text", "#0F172A")
                }
                Label {
                    text: root.nextAction()
                    color: root.themeColor("accent", "#2563EB")
                }
            }
        }

        GroupBox {
            title: "Action Panel"

            Row {
                spacing: 4

                Button {
                    text: "Go User"
                    onClicked: root.navigateTo("user")
                }
                Button {
                    text: "Go Calibration"
                    onClicked: root.navigateTo("calibration")
                }
                Button {
                    text: "Go Training"
                    onClicked: root.navigateTo("training")
                }
                Button {
                    text: "Go Report"
                    onClicked: root.navigateTo("report")
                }
                Button {
                    text: "Go Diagnostics"
                    onClicked: root.navigateTo("diagnostics")
                }
                Button {
                    text: "Refresh"
                    onClicked: root.invokeNative("app.refresh_now")
                }
            }
        }

        GroupBox {
            title: "Page Commands"

            Label {
                text: root.commandSummary
                wrapMode: Text.WordWrap
                color: root.themeColor("text", "#0F172A")
            }
        }

        PageFeedbackPanel {
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            feedbackStyleObj: root.componentStyleObj.feedback_panel || ({})
            pageId: "home"
            lastCommand: root.safeText(root.controlStateObj.last_command)
            lastResult: root.safeText(root.controlStateObj.last_command_result)
            lastError: root.safeText(root.controlStateObj.last_command_error)
        }
    }
}

// Page Feedback
