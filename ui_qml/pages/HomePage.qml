import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root

    property var guiBridge: null
    property var appStateObj: ({})
    property var sessionObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})

    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var renderResourcesObj: ({})
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property string commandSummary: ""
    property bool task26DesktopPilotEnabled: true
    property bool task26LegacyFallbackVisible: false

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

    function task26HomeLayoutPayload() {
        var resources = root.renderResourcesObj || ({})
        return resources.task26_home_layout_payload || ({})
    }

    function task26HomeLayoutStatus() {
        var resources = root.renderResourcesObj || ({})
        return (resources.task26_home_layout_status === undefined || resources.task26_home_layout_status === null)
            ? "n/a"
            : String(resources.task26_home_layout_status)
    }

    function task26HomeLayoutSource() {
        var resources = root.renderResourcesObj || ({})
        return (resources.task26_home_layout_source === undefined || resources.task26_home_layout_source === null)
            ? "n/a"
            : String(resources.task26_home_layout_source)
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: root.themeColor("background", "#F8FAFC")
    }

    Item {
        id: task26HomeDesktopPilotOverlay
        anchors.fill: parent
        anchors.margins: 6
        z: 100
        visible: root.task26DesktopPilotEnabled
        enabled: root.task26DesktopPilotEnabled

        DesktopLayoutPreview {
            id: task26HomeDesktopPrimaryPreview
            anchors.fill: parent
            layoutPayload: root.task26HomeLayoutPayload()
            previewTitle: "TASK26 Home Desktop Pilot"
            previewSubtitle: "primary desktop card layer · legacy fallback: " + String(root.task26LegacyFallbackVisible)
            payloadStatusText: root.task26HomeLayoutStatus()
            payloadSourceText: root.task26HomeLayoutSource()
            guiBridge: root.guiBridge
            appStateObj: root.appStateObj
            runtimeSnapshotObj: root.runtimeObj
            sessionStateObj: root.sessionObj
            controlStateObj: root.controlStateObj
            gameHudObj: root.gameHudObj
            gameViewObj: root.gameViewObj
            renderResourcesObj: root.renderResourcesObj
        }
    }

    Flickable {
        id: homeScroll
        anchors.fill: parent
        visible: root.task26LegacyFallbackVisible
        enabled: root.task26LegacyFallbackVisible
        clip: true
        contentWidth: width
        contentHeight: homeContent.implicitHeight + 16
        boundsBehavior: Flickable.StopAtBounds

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }

        Column {
            id: homeContent
            width: homeScroll.width
            spacing: 6

        PageHeader {
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            headerStyleObj: root.componentStyleObj.header || ({})
            titleText: "Home"
            subtitleText: "Professional overview page"
        }

        GroupBox {
            title: "TASK26 Home Desktop Pilot"
            width: parent.width
            visible: root.task26DesktopPilotEnabled

            DesktopLayoutPreview {
                id: task26HomeDesktopPilotPreview
                width: parent.width
                height: 620
                layoutPayload: root.task26HomeLayoutPayload()
                previewTitle: "Home Desktop Pilot"
                previewSubtitle: "style-capable desktop card layout"
                payloadStatusText: root.task26HomeLayoutStatus()
                payloadSourceText: root.task26HomeLayoutSource()
                guiBridge: root.guiBridge
                appStateObj: root.appStateObj
                runtimeSnapshotObj: root.runtimeObj
                sessionStateObj: root.sessionObj
                controlStateObj: root.controlStateObj
                gameHudObj: root.gameHudObj
                gameViewObj: root.gameViewObj
                renderResourcesObj: root.renderResourcesObj
            }
        }

        GroupBox {
            title: "State Summary"
            visible: root.task26LegacyFallbackVisible

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
            visible: root.task26LegacyFallbackVisible

            Row {
                spacing: 4

                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                    text: "Go User"
                    onClicked: root.navigateTo("user")
                }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                    text: "Go Calibration"
                    onClicked: root.navigateTo("calibration")
                }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                    text: "Go Training"
                    onClicked: root.navigateTo("training")
                }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                    text: "Go Report"
                    onClicked: root.navigateTo("report")
                }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                    text: "Go Diagnostics"
                    onClicked: root.navigateTo("diagnostics")
                }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                    text: "Refresh"
                    onClicked: root.invokeNative("app.refresh_now")
                }
            }
        }

        GroupBox {
            title: "Page Commands"
            visible: root.task26LegacyFallbackVisible

            Label {
                text: root.commandSummary
                wrapMode: Text.WordWrap
                color: root.themeColor("text", "#0F172A")
            }
        }

        PageFeedbackPanel {
            visible: root.task26LegacyFallbackVisible
            renderResourcesObj: root.renderResourcesObj
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
}

// Page Feedback
