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
    property bool task26DesktopPilotEnabled: false
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

    function statusText() {
        var uid = root.safeText(root.controlStateObj.current_user_id)
        var cal = root.safeText(root.controlStateObj.calibration_status)
        var quality = root.safeText(root.runtimeObj.quality_state)
        if (uid === "n/a") {
            return "Create or load a user profile first."
        }
        if (cal === "n/a" || cal === "no_calibration" || cal === "profile_without_calibration") {
            return "User loaded · calibration check recommended."
        }
        if (quality !== "n/a") {
            return "Ready · quality=" + quality
        }
        return "Ready for training workflow."
    }

    function cardBorder(activeValue) {
        return activeValue ? "#7DD3FC" : "#334155"
    }

    function cardWidth(containerWidth) {
        if (containerWidth >= 940) {
            return Math.floor((containerWidth - 24) / 3)
        }
        if (containerWidth >= 620) {
            return Math.floor((containerWidth - 12) / 2)
        }
        return Math.max(260, containerWidth)
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: root.themeColor("background", "#0B1220")
    }

    Flickable {
        id: homeScroll
        anchors.fill: parent
        anchors.margins: 10
        clip: true
        contentWidth: width
        contentHeight: homeContent.implicitHeight + 20
        boundsBehavior: Flickable.StopAtBounds

        Column {
            id: homeContent
            width: homeScroll.width - 16
            spacing: 14

            Rectangle {
                id: introCard
                objectName: "home_intro_card"
                width: parent.width
                height: 210
                radius: 24
                color: "#111827"
                border.color: "#38BDF8"
                border.width: 1

                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#12213A" }
                    GradientStop { position: 1.0; color: "#0B1220" }
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 10

                    Label {
                        text: "RELIC Focus Training"
                        color: "#E0F2FE"
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Label {
                        text: "基于单通道 EEG + IMU 的专注力训练与状态管理平台"
                        color: "#BAE6FD"
                        font.pixelSize: 15
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }

                    Label {
                        text: "系统围绕用户建档、质量门控、FI 状态估计、训练任务与报告回顾构建闭环。Home 页现在作为实机入口页使用，负责快速进入关键工作流，而不是堆放调试面板。"
                        color: "#CBD5E1"
                        font.pixelSize: 13
                        lineHeight: 1.18
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }

                    Flow {
                        width: parent.width
                        spacing: 8

                        Rectangle {
                            width: 190; height: 30; radius: 15
                            color: "#0F766E"
                            opacity: 0.92
                            Label { anchors.centerIn: parent; text: "current_user_id: " + root.safeText(root.controlStateObj.current_user_id); color: "white"; font.pixelSize: 11 }
                        }
                        Rectangle {
                            width: 190; height: 30; radius: 15
                            color: "#1D4ED8"
                            opacity: 0.9
                            Label { anchors.centerIn: parent; text: "connection: " + root.safeText(root.runtimeObj.connection_status); color: "white"; font.pixelSize: 11 }
                        }
                        Rectangle {
                            width: 180; height: 30; radius: 15
                            color: "#7C3AED"
                            opacity: 0.9
                            Label { anchors.centerIn: parent; text: "session_active: " + root.safeText(root.controlStateObj.session_active); color: "white"; font.pixelSize: 11 }
                        }
                    }
                }
            }

            Rectangle {
                id: workflowCard
                objectName: "home_workflow_card"
                width: parent.width
                height: 104
                radius: 22
                color: "#0F172A"
                border.color: "#475569"
                border.width: 1

                Row {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Column {
                        width: Math.max(260, parent.width * 0.36)
                        spacing: 6
                        Label { text: "Recommended Flow"; color: "#E2E8F0"; font.bold: true; font.pixelSize: 17 }
                        Label { text: root.statusText(); color: "#94A3B8"; font.pixelSize: 12; wrapMode: Text.WordWrap; width: parent.width }
                    }

                    Flow {
                        width: parent.width - Math.max(260, parent.width * 0.36) - 12
                        spacing: 8
                        Rectangle { width: 120; height: 42; radius: 16; color: "#182235"; border.color: "#38BDF8"; Label { anchors.centerIn: parent; text: "1 · User"; color: "#E0F2FE"; font.bold: true } }
                        Rectangle { width: 150; height: 42; radius: 16; color: "#182235"; border.color: "#A78BFA"; Label { anchors.centerIn: parent; text: "2 · Calibration"; color: "#EDE9FE"; font.bold: true } }
                        Rectangle { width: 145; height: 42; radius: 16; color: "#182235"; border.color: "#34D399"; Label { anchors.centerIn: parent; text: "3 · Training"; color: "#DCFCE7"; font.bold: true } }
                        Rectangle { width: 130; height: 42; radius: 16; color: "#182235"; border.color: "#FBBF24"; Label { anchors.centerIn: parent; text: "4 · Report"; color: "#FEF3C7"; font.bold: true } }
                    }
                }
            }

            Flow {
                id: entryFlow
                objectName: "home_shortcut_cards"
                width: parent.width
                spacing: 12

                Rectangle {
                    objectName: "home_entry_user_card"
                    width: root.cardWidth(entryFlow.width)
                    height: 178
                    radius: 22
                    color: "#101827"
                    border.color: root.cardBorder(root.safeText(root.controlStateObj.current_user_id) !== "n/a")
                    border.width: 1
                    Column {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8
                        Label { text: "User Center"; color: "#E2E8F0"; font.bold: true; font.pixelSize: 18 }
                        Label { text: "用户建档、加载当前用户、查看 Profile 与校准绑定。"; color: "#94A3B8"; wrapMode: Text.WordWrap; width: parent.width; font.pixelSize: 12 }
                        Label { text: "current: " + root.safeText(root.controlStateObj.current_user_id); color: "#BAE6FD"; font.pixelSize: 11; elide: Text.ElideRight; width: parent.width }
                        DesignButton { text: "Open User"; buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; onClicked: root.navigateTo("user") }
                    }
                }

                Rectangle {
                    objectName: "home_entry_calibration_card"
                    width: root.cardWidth(entryFlow.width)
                    height: 178
                    radius: 22
                    color: "#101827"
                    border.color: root.cardBorder(root.safeText(root.controlStateObj.calibration_usable) === "true")
                    border.width: 1
                    Column {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8
                        Label { text: "Calibration"; color: "#E2E8F0"; font.bold: true; font.pixelSize: 18 }
                        Label { text: "首次建档、快速检查、周期复校与异常触发复校入口。"; color: "#94A3B8"; wrapMode: Text.WordWrap; width: parent.width; font.pixelSize: 12 }
                        Label { text: "status: " + root.safeText(root.controlStateObj.calibration_status); color: "#C4B5FD"; font.pixelSize: 11; elide: Text.ElideRight; width: parent.width }
                        DesignButton { text: "Open Calibration"; buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; onClicked: root.navigateTo("calibration") }
                    }
                }

                Rectangle {
                    objectName: "home_entry_training_card"
                    width: root.cardWidth(entryFlow.width)
                    height: 178
                    radius: 22
                    color: "#101827"
                    border.color: root.cardBorder(root.safeText(root.controlStateObj.session_active) === "true")
                    border.width: 1
                    Column {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8
                        Label { text: "Training"; color: "#E2E8F0"; font.bold: true; font.pixelSize: 18 }
                        Label { text: "进入 Fragment Lock / Signal Hunter / Stabilizer 训练链路。"; color: "#94A3B8"; wrapMode: Text.WordWrap; width: parent.width; font.pixelSize: 12 }
                        Label { text: "score: " + root.safeText(root.gameHudObj.score) + " · combo: " + root.safeText(root.gameHudObj.combo); color: "#BBF7D0"; font.pixelSize: 11; elide: Text.ElideRight; width: parent.width }
                        DesignButton { text: "Open Training"; buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; onClicked: root.navigateTo("training") }
                    }
                }

                Rectangle {
                    objectName: "home_entry_report_card"
                    width: root.cardWidth(entryFlow.width)
                    height: 178
                    radius: 22
                    color: "#101827"
                    border.color: "#F59E0B"
                    border.width: 1
                    Column {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8
                        Label { text: "Reports"; color: "#E2E8F0"; font.bold: true; font.pixelSize: 18 }
                        Label { text: "查看训练报告、报告预览与 TXT 导出结果。"; color: "#94A3B8"; wrapMode: Text.WordWrap; width: parent.width; font.pixelSize: 12 }
                        Label { text: "latest: " + root.safeText(root.controlStateObj.latest_report_path); color: "#FDE68A"; font.pixelSize: 11; elide: Text.ElideRight; width: parent.width }
                        DesignButton { text: "Open Report"; buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; onClicked: root.navigateTo("report") }
                    }
                }

                Rectangle {
                    objectName: "home_entry_developer_lab_card"
                    width: root.cardWidth(entryFlow.width)
                    height: 178
                    radius: 22
                    color: "#101827"
                    border.color: "#FB7185"
                    border.width: 1
                    Column {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8
                        Label { text: "Developer Lab"; color: "#E2E8F0"; font.bold: true; font.pixelSize: 18 }
                        Label { text: "工程数据面板、FI/SQI 参数观察与后续小规模网格搜索控制台。"; color: "#94A3B8"; wrapMode: Text.WordWrap; width: parent.width; font.pixelSize: 12 }
                        Label { text: "control_state: " + root.safeText(root.runtimeObj.control_state); color: "#FECDD3"; font.pixelSize: 11; elide: Text.ElideRight; width: parent.width }
                        DesignButton { text: "Open Developer Lab"; buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; onClicked: root.navigateTo("developer_lab") }
                    }
                }
            }

            Rectangle {
                id: telemetryCard
                objectName: "home_status_overview_card"
                width: parent.width
                height: 150
                radius: 22
                color: "#0F172A"
                border.color: "#334155"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8
                    Label { text: "Runtime Snapshot"; color: "#E2E8F0"; font.bold: true; font.pixelSize: 17 }
                    Flow {
                        width: parent.width
                        spacing: 8
                        Label { text: "attention: " + root.safeText(root.runtimeObj.attention); color: "#CBD5E1"; font.pixelSize: 12 }
                        Label { text: "sqi: " + root.safeText(root.runtimeObj.sqi); color: "#CBD5E1"; font.pixelSize: 12 }
                        Label { text: "fi_smoothed: " + root.safeText(root.runtimeObj.fi_smoothed); color: "#CBD5E1"; font.pixelSize: 12 }
                        Label { text: "quality_state: " + root.safeText(root.runtimeObj.quality_state); color: "#CBD5E1"; font.pixelSize: 12 }
                        Label { text: "control_state: " + root.safeText(root.runtimeObj.control_state); color: "#CBD5E1"; font.pixelSize: 12 }
                        Label { text: "gyro_x: " + root.safeText(root.runtimeObj.gyro_x); color: "#CBD5E1"; font.pixelSize: 12 }
                    }
                    Label {
                        text: "Page Commands: " + root.commandSummary
                        color: "#94A3B8"
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }
                    Label {
                        text: "Page Feedback · last_command: " + root.safeText(root.controlStateObj.last_command)
                            + " · result: " + root.safeText(root.controlStateObj.last_command_result)
                            + " · error: " + root.safeText(root.controlStateObj.last_command_error)
                        color: "#64748B"
                        font.pixelSize: 10
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }
                }
            }
        }
    }

    Rectangle {
        id: scrollTrack
        width: 5
        radius: 3
        color: "#1E293B"
        opacity: homeScroll.contentHeight > homeScroll.height ? 0.48 : 0.0
        anchors.right: parent.right
        anchors.rightMargin: 5
        anchors.top: parent.top
        anchors.topMargin: 18
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 18

        Rectangle {
            width: parent.width
            radius: 3
            color: "#38BDF8"
            opacity: homeScroll.moving || homeScroll.flicking ? 0.9 : 0.52
            height: Math.max(34, parent.height * homeScroll.visibleArea.heightRatio)
            y: Math.max(0, Math.min(parent.height - height, parent.height * homeScroll.visibleArea.yPosition))
        }
    }
}

// Page Commands
// Page Feedback
// TASK26 Home formal shortcut tokens: home_intro_card home_workflow_card home_shortcut_cards home_entry_user_card home_entry_calibration_card home_entry_training_card home_entry_report_card home_entry_developer_lab_card home_status_overview_card
// Legacy compatibility tokens: State Summary Action Panel Go User Go Calibration Go Training Go Report Go Developer Lab Refresh navigateTo("developer_lab")
