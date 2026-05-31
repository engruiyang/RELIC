import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: reportPage

    property var guiBridge: null
    property var runtimeObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})
    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var renderResourcesObj: ({})
    property bool task26DesktopPilotEnabled: true
    property bool task26LegacyFallbackVisible: false

    function task26ReportLayoutPayload() {
        var resources = reportPage.renderResourcesObj || ({})
        return resources.task26_report_layout_payload || ({})
    }


    property var appStateObj: ({})
    property var controlStateObj: ({})
    property var sessionObj: ({})
    property string commandSummary: ""

    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""

    property string activePanel: "summary"
    property var actionResultObj: ({})
    property var reportSummaryObj: ({})
    property var sessionItems: []
    property var sessionIdModel: []
    property var sessionDetailObj: ({})
    property string selectedSessionId: ""
    property string reportActionText: "No report action yet."

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    function currentUserId() {
        var uid = s(controlStateObj.current_user_id)
        if (uid !== "n/a") {
            return uid
        }
        uid = s(appStateObj.current_user_id)
        return uid === "n/a" ? "" : uid
    }

    function safeJsonParse(t) {
        try {
            return JSON.parse(t || "{}")
        } catch (e) {
            return {"status": "parse_error", "message": "invalid action result", "raw": String(t)}
        }
    }

    function pretty(v) {
        try {
            return JSON.stringify(v || {}, null, 2)
        } catch (e) {
            return String(v)
        }
    }

    function pick(id, status, mode, nativeActionId) {
        selectedCommandId = id
        selectedStatus = status
        selectedExecutionMode = mode
        selectedNativeActionId = nativeActionId
    }

    function reportItemsFrom(obj) {
        if (!obj) {
            return []
        }
        if (obj.items && Array.isArray(obj.items)) {
            return obj.items
        }
        if (obj.sessions && Array.isArray(obj.sessions)) {
            return obj.sessions
        }
        if (obj.result && obj.result.items && Array.isArray(obj.result.items)) {
            return obj.result.items
        }
        if (obj.result && obj.result.sessions && Array.isArray(obj.result.sessions)) {
            return obj.result.sessions
        }
        return []
    }

    function updateSessionModels(items) {
        sessionItems = items || []
        var ids = []
        for (var i = 0; i < sessionItems.length; i++) {
            var sid = s(sessionItems[i].session_id)
            if (sid !== "n/a") {
                ids.push(sid)
            }
        }
        sessionIdModel = ids
        if ((selectedSessionId === "" || selectedSessionId === "n/a") && ids.length > 0) {
            selectedSessionId = ids[0]
        }
    }

    function formatSessionList(items) {
        if (!items || items.length === 0) {
            return "No sessions found."
        }
        var lines = []
        for (var i = 0; i < items.length; i++) {
            var item = items[i]
            lines.push((i + 1) + ". "
                + s(item.session_id)
                + " | user=" + s(item.user_id)
                + " | game=" + s(item.game_id)
                + " | status=" + s(item.status)
                + " | score=" + s(item.score)
                + " | report_path=" + s(item.report_path))
        }
        return lines.join("\n")
    }

    function formatReportSummary(obj) {
        var src = obj || reportSummaryObj || {}
        if (src.result && typeof src.result === "object") {
            src = src.result
        }
        return "current_user_id: " + s(src.user_id || currentUserId())
            + "\nlatest_session_id: " + s(src.latest_session_id || sessionObj.session_id)
            + "\nlatest_report_path: " + s(src.latest_report_path || sessionObj.latest_report_path || sessionObj.report_path || controlStateObj.latest_report_path)
            + "\nreport_available: " + s(src.report_available)
            + "\nreason: " + s(src.reason || src.message)
    }

    function formatSessionDetail(obj) {
        var d = obj || {}
        if (d.result && typeof d.result === "object") {
            d = d.result
        }
        return "session_id: " + s(d.session_id)
            + "\nuser_id: " + s(d.user_id)
            + "\ngame_id: " + s(d.game_id)
            + "\nstatus: " + s(d.status)
            + "\nscore: " + s(d.score)
            + "\nduration_sec: " + s(d.duration_sec)
            + "\nbehavior_sample_count: " + s(d.behavior_sample_count)
            + "\ngame_event_count: " + s(d.game_event_count)
            + "\nwarning_count: " + s(d.warning_count)
            + "\nerror_count: " + s(d.error_count)
            + "\nlog_path: " + s(d.log_path)
            + "\nreport_path: " + s(d.report_path)
            + "\n\nreport_preview:\n" + s(d.report_preview)
    }

    function invokeReport(actionId, payload) {
        var finalPayload = payload || {}
        if (finalPayload.user_id === undefined) {
            finalPayload.user_id = currentUserId()
        }
        var raw = "{}"
        if (typeof guiBridge !== "undefined" && guiBridge) {
            raw = guiBridge.invokeAction(actionId, JSON.stringify(finalPayload))
        } else {
            raw = JSON.stringify({"action_id": actionId, "status": "bridge_missing", "message": "guiBridge unavailable"})
        }

        var obj = safeJsonParse(raw)
        actionResultObj = obj
        reportActionText = pretty(obj)
        selectedCommandId = actionId
        selectedStatus = s(obj.status)
        selectedExecutionMode = "native"
        selectedNativeActionId = actionId

        if (actionId === "report.refresh") {
            reportSummaryObj = obj.result || obj.detail || obj.report || obj
            activePanel = "summary"
        } else if (actionId === "report.list") {
            var items = reportItemsFrom(obj)
            updateSessionModels(items)
            activePanel = "list"
        } else if (actionId === "report.show") {
            sessionDetailObj = obj.detail || obj.result || obj.report || obj
            activePanel = "detail"
        } else {
            activePanel = "result"
        }
        return obj
    }

    function refreshReport() {
        invokeReport("report.refresh", {"user_id": currentUserId()})
    }

    function listSessions() {
        invokeReport("report.list", {"user_id": currentUserId()})
    }

    function showSelectedSession() {
        if (selectedSessionId === "" || selectedSessionId === "n/a") {
            var obj = {
                "action_id": "report.show",
                "status": "missing_input",
                "result": "missing_session_id",
                "message": "missing_session_id",
                "accepted": false
            }
            actionResultObj = obj
            reportActionText = pretty(obj)
            selectedCommandId = "report.show"
            selectedStatus = "missing_input"
            selectedExecutionMode = "native"
            selectedNativeActionId = "report.show"
            activePanel = "result"
            return
        }
        invokeReport("report.show", {"user_id": currentUserId(), "session_id": selectedSessionId})
    }

    function exportReport() {
        if (selectedSessionId === "" || selectedSessionId === "n/a") {
            var obj = {
                "action_id": "report.export",
                "status": "missing_input",
                "result": "missing_session_id",
                "message": "missing_session_id",
                "accepted": false
            }
            actionResultObj = obj
            reportActionText = pretty(obj)
            selectedCommandId = "report.export"
            selectedStatus = "missing_input"
            selectedExecutionMode = "native"
            selectedNativeActionId = "report.export"
            activePanel = "result"
            return
        }
        invokeReport("report.export", {"user_id": currentUserId(), "session_id": selectedSessionId})
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: reportPage.designThemeObj
        styleObj: reportPage.pageStyleObj
        renderResourcesObj: reportPage.renderResourcesObj
        fallbackColor: (reportPage.designThemeObj.colors && reportPage.designThemeObj.colors.background) ? reportPage.designThemeObj.colors.background : "#F8FAFC"
    }


    Item {
        id: task26ReportDesktopPilotOverlay
        anchors.fill: parent
        anchors.margins: 6
        z: 100
        visible: reportPage.task26DesktopPilotEnabled
        enabled: reportPage.task26DesktopPilotEnabled

        DesktopLayoutPreview {
            id: task26ReportDesktopLayoutPreview
            anchors.fill: parent
            layoutPayload: reportPage.task26ReportLayoutPayload()
            previewTitle: "TASK26 Report Desktop Pilot"
            previewSubtitle: "Full-area card desktop pilot · legacy fallback: " + String(reportPage.task26LegacyFallbackVisible)
            payloadStatusText: String((reportPage.renderResourcesObj || ({})).task26_report_layout_status || "n/a")
            payloadSourceText: String((reportPage.renderResourcesObj || ({})).task26_report_layout_source || "n/a")
            guiBridge: reportPage.guiBridge
            appStateObj: reportPage.appStateObj
            runtimeSnapshotObj: reportPage.runtimeObj
            sessionStateObj: reportPage.sessionObj
            controlStateObj: reportPage.controlStateObj
            gameHudObj: reportPage.gameHudObj
            gameViewObj: reportPage.gameViewObj
            renderResourcesObj: reportPage.renderResourcesObj
        }
    }


    ScrollView {
        id: legacyReportLayer
        anchors.fill: parent
        visible: reportPage.task26LegacyFallbackVisible
        enabled: reportPage.task26LegacyFallbackVisible
        clip: true

        Column {
            width: reportPage.width - 16
            spacing: 8

            PageHeader {
            renderResourcesObj: reportPage.renderResourcesObj
            designThemeObj: reportPage.designThemeObj
            componentStyleObj: reportPage.componentStyleObj
            headerStyleObj: reportPage.componentStyleObj.header || ({})
                titleText: "Report Page"
                subtitleText: "Session/report viewer for the current user"
            }

            GroupBox {
                title: "Report Readiness"
                width: parent.width

                Column {
                    spacing: 4
                    Label { text: "current_user_id: " + s(reportPage.currentUserId()) }
                    Label { text: "latest_session_id: " + s(sessionObj.session_id || controlStateObj.current_session_id) }
                    Label { text: "latest_report_path: " + s(sessionObj.latest_report_path || sessionObj.report_path || controlStateObj.latest_report_path) }
                    Label { text: "report_available: " + (s(sessionObj.latest_report_path || sessionObj.report_path || controlStateObj.latest_report_path) !== "n/a") }
                    Label { text: "reason: " + (s(sessionObj.latest_report_path || sessionObj.report_path || controlStateObj.latest_report_path) === "n/a" ? "no_report_available" : "report_available") }
                }
            }

            GroupBox {
                title: "Report Page Actions"
                width: parent.width

                Flow {
                    width: parent.width
                    spacing: 6

                    DesignButton { buttonStyleObj: reportPage.componentStyleObj.button || ({}); themeObj: reportPage.designThemeObj; renderResourcesObj: reportPage.renderResourcesObj;
                        text: "Refresh Report"
                        onClicked: reportPage.refreshReport()
                    }

                    DesignButton { buttonStyleObj: reportPage.componentStyleObj.button || ({}); themeObj: reportPage.designThemeObj; renderResourcesObj: reportPage.renderResourcesObj;
                        text: "List Sessions"
                        onClicked: reportPage.listSessions()
                    }

                    DesignButton { buttonStyleObj: reportPage.componentStyleObj.button || ({}); themeObj: reportPage.designThemeObj; renderResourcesObj: reportPage.renderResourcesObj;
                        text: "Show Session"
                        onClicked: reportPage.showSelectedSession()
                    }

                    DesignButton { buttonStyleObj: reportPage.componentStyleObj.button || ({}); themeObj: reportPage.designThemeObj; renderResourcesObj: reportPage.renderResourcesObj;
                        text: "Show Selected Session"
                        onClicked: reportPage.showSelectedSession()
                    }

                    DesignButton { buttonStyleObj: reportPage.componentStyleObj.button || ({}); themeObj: reportPage.designThemeObj; renderResourcesObj: reportPage.renderResourcesObj;
                        text: "Latest Report"
                        onClicked: reportPage.refreshReport()
                    }

                    DesignButton { buttonStyleObj: reportPage.componentStyleObj.button || ({}); themeObj: reportPage.designThemeObj; renderResourcesObj: reportPage.renderResourcesObj;
                        text: "Export Report"
                        onClicked: reportPage.exportReport()
                    }

                    DesignButton { buttonStyleObj: reportPage.componentStyleObj.button || ({}); themeObj: reportPage.designThemeObj; renderResourcesObj: reportPage.renderResourcesObj;
                        text: "Open Path Manual"
                        onClicked: reportPage.pick("report.open_path_manual", "manual", "manual", "")
                    }
                }
            }

            GroupBox {
                title: "Latest Report"
                width: parent.width
                visible: activePanel === "summary" || activePanel === "result"

                TextArea {
                    width: parent.width
                    height: Math.min(220, Math.max(120, contentHeight + 32))
                    readOnly: true
                    wrapMode: TextEdit.Wrap
                    text: reportPage.formatReportSummary(reportSummaryObj)
                }
            }

            GroupBox {
                title: "Session List"
                width: parent.width
                visible: activePanel === "list" || sessionIdModel.length > 0

                Column {
                    width: parent.width
                    spacing: 6

                    Label { text: "items_count: " + s(sessionItems.length) }
                    Label { text: "selected_session_id" }
                    Label {
                        text: reportPage.selectedSessionId === "" || reportPage.selectedSessionId === "n/a"
                            ? "missing_session_id"
                            : "selected: " + reportPage.selectedSessionId
                        wrapMode: Text.WordWrap
                    }

                    ComboBox {
                        width: Math.min(parent.width - 20, 720)
                        model: reportPage.sessionIdModel
                        currentIndex: reportPage.sessionIdModel.indexOf(reportPage.selectedSessionId)
                        onActivated: function(index) {
                            if (index >= 0 && index < reportPage.sessionIdModel.length) {
                                reportPage.selectedSessionId = reportPage.sessionIdModel[index]
                            }
                        }
                    }

                    TextArea {
                        width: parent.width
                        height: Math.min(300, Math.max(160, contentHeight + 32))
                        readOnly: true
                        wrapMode: TextEdit.Wrap
                        text: reportPage.formatSessionList(sessionItems)
                    }
                }
            }

            GroupBox {
                title: "Session Detail"
                width: parent.width
                visible: activePanel === "detail"

                TextArea {
                    width: parent.width
                    height: Math.min(520, Math.max(260, contentHeight + 36))
                    readOnly: true
                    wrapMode: TextEdit.Wrap
                    text: reportPage.formatSessionDetail(sessionDetailObj)
                }
            }

            GroupBox {
                title: "Report Action Result"
                width: parent.width

                TextArea {
                    width: parent.width
                    height: Math.min(320, Math.max(140, contentHeight + 32))
                    readOnly: true
                    wrapMode: TextEdit.Wrap
                    text: reportPage.reportActionText
                }
            }

            GroupBox {
                title: "Page Commands"
                width: parent.width

                Label {
                    text: commandSummary
                    wrapMode: Text.WordWrap
                }
            }

            PageFeedbackPanel {
            renderResourcesObj: reportPage.renderResourcesObj
            designThemeObj: reportPage.designThemeObj
            componentStyleObj: reportPage.componentStyleObj
            feedbackStyleObj: reportPage.componentStyleObj.feedback_panel || ({})
                pageId: "report"
                selectedCommandId: reportPage.selectedCommandId
                selectedStatus: reportPage.selectedStatus
                selectedExecutionMode: reportPage.selectedExecutionMode
                selectedNativeActionId: reportPage.selectedNativeActionId
                lastCommand: s(controlStateObj.last_command)
                lastResult: s(controlStateObj.last_command_result)
                lastError: s(controlStateObj.last_command_error)
            }
        }
    }
}

// Page Feedback
