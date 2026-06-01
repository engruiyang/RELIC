import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root

    property var guiBridge: null
    property var appStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})
    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var renderResourcesObj: ({})
    property bool task26DesktopPilotEnabled: true
    property bool task26LegacyFallbackVisible: false

    function task26CalibrationLayoutPayload() {
        var resources = root.renderResourcesObj || ({})
        return resources.task26_calibration_layout_payload || ({})
    }


    property var controlStateObj: ({})
    property string commandSummary: ""

    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""

    property string activePanel: "status"
    property var lastActionObj: ({})
    property var statusObj: ({})
    property var detailObj: ({})
    property var historyItems: []
    property var calibrationIds: []
    property string selectedCalibrationId: ""
    property int selectedCalibrationIndex: 0
    property string historyText: "No calibration records."
    property string detailText: "No calibration detail available."
    property bool calibrationRunning: false
    property string calibrationProgressText: "Calibration has not started from GUI."
    property string calibrationProgressStatus: "idle"
    property string calibrationProgressPhase: "n/a"
    property string calibrationStartCommand: "n/a"
    property int calibrationOutputCount: 0

    signal invokeNative(string actionId)

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    function currentUserId() {
        return s(controlStateObj.current_user_id, "") === "n/a" ? "" : String(controlStateObj.current_user_id || "")
    }

    function hasCurrentUser() {
        return currentUserId() !== "" && currentUserId() !== "n/a"
    }

    function safeJsonParse(t) {
        try {
            return JSON.parse(t || "{}")
        } catch(e) {
            return ({"action_id": "parse_error", "status": "parse_error", "message": "invalid_json"})
        }
    }

    function setFeedback(actionId, status, mode, nativeActionId) {
        selectedCommandId = actionId
        selectedStatus = status
        selectedExecutionMode = mode
        selectedNativeActionId = nativeActionId
    }

    function formatObject(obj) {
        if (!obj) {
            return "n/a"
        }
        var keys = Object.keys(obj)
        if (keys.length === 0) {
            return "n/a"
        }
        var lines = []
        for (var i = 0; i < keys.length; i++) {
            var k = keys[i]
            var v = obj[k]
            if (v === undefined || v === null) {
                lines.push(k + ": n/a")
            } else if (typeof v === "object") {
                lines.push(k + ": " + JSON.stringify(v, null, 2))
            } else {
                lines.push(k + ": " + String(v))
            }
        }
        return lines.length > 0 ? lines.join("\n") : JSON.stringify(obj, null, 2)
    }

    function formatPhasePrompts(prompts) {
        var items = prompts || []
        if (!items || items.length === 0) {
            return "No phase prompt data yet."
        }
        var lines = []
        for (var i = 0; i < items.length; i++) {
            var item = items[i] || ({})
            lines.push("[" + s(item.phase) + "] " + s(item.title))
            lines.push("  " + s(item.user_instruction))
            lines.push("  " + s(item.avoid_instruction))
            lines.push("  " + s(item.duration_hint))
        }
        return lines.join("\n")
    }

    function formatOutputTail(lines) {
        var items = lines || []
        if (!items || items.length === 0) {
            return "No calibration CLI output yet."
        }
        return items.join("\n")
    }

    function formatCalibrationProgress(progress) {
        var p = progress || ({})
        var promptText = p.phase_prompt_text || p.operator_guidance || formatPhasePrompts(p.phase_prompts)
        var outputText = p.output_text || formatOutputTail(p.output_tail)
        var currentDetail = p.current_phase_detail ? formatObject(p.current_phase_detail) : "n/a"
        return "Operator Phase Prompts\n"
               + promptText
               + "\n\nCurrent Phase Detail\n"
               + currentDetail
               + "\n\nCLI Output Tail\n"
               + outputText
    }

    function normalizeCalibrationItem(item, index) {
        var id = item.calibration_id || item.id || item.profile_id || ("calibration_" + String(index + 1))
        return String(id)
    }

    function updateHistory(items) {
        historyItems = items || []
        var ids = []
        var lines = []
        for (var i = 0; i < historyItems.length; i++) {
            var item = historyItems[i] || ({})
            var id = normalizeCalibrationItem(item, i)
            ids.push(id)
            lines.push((i + 1) + ". " + id
                       + " | type=" + s(item.calibration_type || item.type)
                       + " | valid=" + s(item.valid)
                       + " | source=" + s(item.source)
                       + " | created_at=" + s(item.created_at))
        }
        calibrationIds = ids
        if (ids.length > 0) {
            if (selectedCalibrationId === "" || ids.indexOf(selectedCalibrationId) < 0) {
                selectedCalibrationId = ids[0]
                selectedCalibrationIndex = 0
            }
            historyText = lines.join("\n")
        } else {
            selectedCalibrationId = ""
            selectedCalibrationIndex = 0
            historyText = "No calibration records."
        }
    }

    function updateDetail(obj) {
        detailObj = obj || ({})
        if (detailObj.calibration_id !== undefined && detailObj.calibration_id !== null && detailObj.calibration_id !== "") {
            selectedCalibrationId = String(detailObj.calibration_id)
        }
        detailText = formatObject(detailObj)
    }

    function resultStatus(obj) {
        return String((obj && obj.status) ? obj.status : "unknown")
    }

    function calibrationStatusKeepsPanel(statusText) {
        var st = String(statusText || "").toLowerCase()
        return st === "started"
               || st === "running"
               || st === "already_running"
               || st === "guidance_running"
               || st === "start_guidance"
    }

    function progressSaysRunning(progress) {
        var p = progress || ({})
        var st = String(p.status || "").toLowerCase()
        if (p.running === true || String(p.running).toLowerCase() === "true") {
            return true
        }
        return calibrationStatusKeepsPanel(st)
    }

    function invokeCalibration(actionId, payload, nextPanel) {
        var userId = currentUserId()
        var data = payload || ({})
        if (userId !== "" && data.user_id === undefined) {
            data.user_id = userId
        }
        setFeedback(actionId, "native", "native", actionId)
        if (!guiBridge) {
            lastActionObj = {"action_id": actionId, "status": "bridge_missing", "message": "bridge_missing"}
            activePanel = "result"
            return
        }
        var raw = guiBridge.invokeAction(actionId, JSON.stringify(data))
        var obj = safeJsonParse(raw)
        lastActionObj = obj
        selectedStatus = resultStatus(obj)

        if (actionId === "calibration.status") {
            statusObj = obj.calibration || obj.detail || obj.result || obj
            activePanel = nextPanel || "status"
        } else if (actionId === "calibration.list") {
            var source = obj.items || obj.calibrations || (obj.result ? (obj.result.items || obj.result.calibrations) : []) || []
            updateHistory(source)
            activePanel = nextPanel || "list"
        } else if (actionId === "calibration.latest") {
            updateDetail(obj.detail || obj.calibration || obj.result || obj)
            activePanel = nextPanel || "detail"
        } else if (actionId === "calibration.show") {
            updateDetail(obj.detail || obj.calibration || obj.result || obj)
            activePanel = resultStatus(obj) === "missing_input" ? "list" : (nextPanel || "detail")
        } else if (actionId === "calibration.bind") {
            if (obj.calibration) {
                statusObj = obj.calibration
            }
            activePanel = resultStatus(obj) === "missing_input" ? "list" : (nextPanel || "status")
        } else if (actionId === "calibration.start") {
            var progress = obj.progress || obj.result || obj
            calibrationProgressStatus = s(obj.status)
            calibrationProgressPhase = s(progress.current_phase || progress.phase || obj.phase)
            calibrationStartCommand = s(progress.command || obj.command || obj.cli_reference)
            calibrationOutputCount = Number(progress.output_count || 0)
            calibrationProgressText = formatCalibrationProgress(progress)
            calibrationRunning = progressSaysRunning(progress) || calibrationStatusKeepsPanel(obj.status)
            activePanel = "progress"
        } else if (actionId === "calibration.poll") {
            var p = obj.progress || obj.result || obj
            calibrationProgressStatus = s(obj.status)
            calibrationProgressPhase = s(p.current_phase || p.phase || obj.phase)
            calibrationStartCommand = s(p.command || obj.command || obj.cli_reference || calibrationStartCommand)
            calibrationOutputCount = Number(p.output_count || calibrationOutputCount)
            calibrationProgressText = formatCalibrationProgress(p)
            calibrationRunning = progressSaysRunning(p) || calibrationStatusKeepsPanel(obj.status)
            activePanel = "progress"
        } else {
            activePanel = nextPanel || "result"
        }
    }

    function requireUserOrShowResult(actionId) {
        if (hasCurrentUser()) {
            return true
        }
        setFeedback(actionId, "missing_user", "native", actionId)
        lastActionObj = {"action_id": actionId, "status": "missing_user", "message": "No current user loaded."}
        activePanel = "result"
        return false
    }

    function doStatus() {
        if (requireUserOrShowResult("calibration.status")) {
            invokeCalibration("calibration.status", ({}), "status")
        }
    }

    function doList() {
        if (requireUserOrShowResult("calibration.list")) {
            invokeCalibration("calibration.list", ({}), "list")
        }
    }

    function doLatest() {
        if (requireUserOrShowResult("calibration.latest")) {
            invokeCalibration("calibration.latest", ({}), "detail")
        }
    }

    function doShowSelected() {
        if (!requireUserOrShowResult("calibration.show")) {
            return
        }
        if (selectedCalibrationId === "") {
            setFeedback("calibration.show", "missing_input", "native", "calibration.show")
            lastActionObj = {"action_id": "calibration.show", "status": "missing_input", "message": "missing_calibration_id"}
            activePanel = "list"
            return
        }
        invokeCalibration("calibration.show", {"calibration_id": selectedCalibrationId}, "detail")
    }

    function doBindSelected() {
        if (!requireUserOrShowResult("calibration.bind")) {
            return
        }
        if (selectedCalibrationId === "") {
            setFeedback("calibration.bind", "missing_input", "native", "calibration.bind")
            lastActionObj = {"action_id": "calibration.bind", "status": "missing_input", "message": "missing_calibration_id"}
            activePanel = "list"
            return
        }
        invokeCalibration("calibration.bind", {"calibration_id": selectedCalibrationId}, "status")
    }

    function doCancel() {
        if (requireUserOrShowResult("calibration.cancel")) {
            invokeCalibration("calibration.cancel", ({}), "result")
        }
    }

    function doStartCalibration() {
        if (requireUserOrShowResult("calibration.start")) {
            calibrationProgressStatus = "requesting"
            calibrationProgressPhase = "phase 1/4"
            calibrationProgressText = "Calibration start requested. Waiting for backend progress...\n\nOperator Phase Prompts will appear below."
            activePanel = "progress"
            invokeCalibration("calibration.start", {"calibration_type": "auto", "source": "ipc"}, "progress")
        }
    }

    function doPollProgress() {
        invokeCalibration("calibration.poll", ({}), "progress")
    }

    function calibrationProgressIsRunning() {
        var state = root.controlStateObj || ({})
        var runningValue = state.calibration_progress_running
        var statusText = String(state.calibration_progress_status || "").toLowerCase()
        if (runningValue === true) {
            return true
        }
        if (String(runningValue).toLowerCase() === "true") {
            return true
        }
        return statusText === "running" || statusText === "guidance_running" || statusText === "started" || statusText === "already_running" || statusText === "start_guidance"
    }

    function refreshDesktopCalibrationFeedback() {
        if (!root.guiBridge) {
            return
        }
        if (calibrationProgressIsRunning()) {
            root.guiBridge.invokeAction("calibration.poll", "{}")
        }
        root.controlStateObj = safeJsonParse(root.guiBridge.controlStateJson)
        root.renderResourcesObj = safeJsonParse(root.guiBridge.renderResourcesJson)
    }

    Timer {
        id: calibrationProgressTimer
        interval: 1000
        running: root.visible && root.task26DesktopPilotEnabled
        repeat: true
        onTriggered: root.refreshDesktopCalibrationFeedback()
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: (root.designThemeObj.colors && root.designThemeObj.colors.background) ? root.designThemeObj.colors.background : "#F8FAFC"
    }


    Item {
        id: task26CalibrationDesktopPilotOverlay
        anchors.fill: parent
        anchors.margins: 6
        z: 100
        visible: root.task26DesktopPilotEnabled
        enabled: root.task26DesktopPilotEnabled

        ScrollView {
            id: task26CalibrationDesktopScrollView
            anchors.fill: parent
            clip: true
            contentWidth: availableWidth
            contentHeight: Math.max(availableHeight, 1040)

            DesktopLayoutPreview {
                id: task26CalibrationDesktopLayoutPreview
                width: Math.max(1, task26CalibrationDesktopScrollView.availableWidth)
                height: Math.max(1040, task26CalibrationDesktopScrollView.availableHeight)
                layoutPayload: root.task26CalibrationLayoutPayload()
                previewTitle: "TASK26 Calibration Desktop Pilot"
                previewSubtitle: "Scrollable formal calibration desktop · legacy fallback: " + String(root.task26LegacyFallbackVisible)
                payloadStatusText: String((root.renderResourcesObj || ({})).task26_calibration_layout_status || "n/a")
                payloadSourceText: String((root.renderResourcesObj || ({})).task26_calibration_layout_source || "n/a")
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
    }



    ScrollView {
        id: calibrationScroller
        anchors.fill: parent
        visible: root.task26LegacyFallbackVisible
        enabled: root.task26LegacyFallbackVisible
        clip: true
        contentWidth: availableWidth

        Column {
            width: Math.max(360, calibrationScroller.availableWidth - 12)
            spacing: 6

        PageHeader {
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            headerStyleObj: root.componentStyleObj.header || ({})
            titleText: "Calibration Page"
            subtitleText: "Calibration requires a current user."
        }

        GroupBox {
            title: "Current User Gate"
            Column {
                spacing: 4
                Label { text: "Calibration requires a current user."; font.bold: true }
                Label { text: hasCurrentUser() ? ("current_user_id: " + currentUserId()) : "No current user loaded." }
                Label { text: hasCurrentUser() ? "User context ready for calibration status/list/detail." : "Please load or create a user in User page first."; wrapMode: Text.WordWrap }
            }
        }

        GroupBox {
            title: "Calibration Page Actions"
            Flow {
                width: parent.width
                spacing: 6
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Calibration Status"; onClicked: root.doStatus() }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "List Calibrations"; onClicked: root.doList() }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Latest Calibration"; onClicked: root.doLatest() }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Show Calibration"; onClicked: root.doShowSelected() }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Bind Calibration"; onClicked: root.doBindSelected() }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Start IPC Calibration"; onClicked: root.doStartCalibration() }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Refresh Calibration Progress"; onClicked: root.doPollProgress() }
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Cancel Calibration"; onClicked: root.doCancel() }
            }
        }

        GroupBox {
            title: "Current User Calibration"
            Column {
                spacing: 3
                Label { text: "current_user_id: " + s(currentUserId()) }
                Label { text: "calibration_status: " + s(statusObj.calibration_status || controlStateObj.calibration_status) }
                Label { text: "last_calibration_id: " + s(statusObj.last_calibration_id || controlStateObj.last_calibration_id) }
                Label { text: "calibration_usable: " + s(statusObj.calibration_usable || controlStateObj.calibration_usable) }
                Label { text: "latest_valid: " + s(statusObj.latest_valid || controlStateObj.latest_valid) }
                Label { text: "failure_reason: " + s(statusObj.failure_reason || controlStateObj.failure_reason) }
                Label { text: "source: " + s(statusObj.source || controlStateObj.source) }
                Label { text: "attention_baseline: " + s(statusObj.attention_baseline || controlStateObj.attention_baseline) }
                Label { text: "gyro_noise_rms: " + s(statusObj.gyro_noise_rms || controlStateObj.gyro_noise_rms) }
            }
        }

        GroupBox {
            title: "Calibration History"
            visible: activePanel === "list" || activePanel === "detail" || activePanel === "status"
            Column {
                spacing: 4
                Label { text: "items_count: " + String(historyItems.length) }
                Label { text: "selected_calibration_id:" }
                ComboBox {
                    id: calibrationChooser
                    width: Math.min(420, Math.max(280, parent.width - 20))
                    model: root.calibrationIds
                    currentIndex: root.selectedCalibrationIndex
                    onActivated: function(index) {
                        root.selectedCalibrationIndex = index
                        root.selectedCalibrationId = currentText
                    }
                }
                TextArea {
                    width: Math.max(320, parent.width - 20)
                    height: Math.min(320, Math.max(130, contentHeight + 36))
                    readOnly: true
                    selectByMouse: true
                    text: root.historyText
                    wrapMode: Text.WordWrap
                }
                Row {
                    spacing: 6
                    DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Show Selected Calibration"; onClicked: root.doShowSelected() }
                    DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Bind Selected Calibration"; onClicked: root.doBindSelected() }
                }
            }
        }

        GroupBox {
            title: "Calibration Detail"
            visible: activePanel === "detail"
            Column {
                spacing: 4
                Label { text: "calibration_id: " + s(detailObj.calibration_id || selectedCalibrationId) }
                Label { text: "valid: " + s(detailObj.valid) }
                Label { text: "calibration_type: " + s(detailObj.calibration_type) }
                Label { text: "attention_baseline: " + s(detailObj.attention_baseline) }
                Label { text: "attention_std: " + s(detailObj.attention_std) }
                Label { text: "gyro_noise_rms: " + s(detailObj.gyro_noise_rms) }
                Label { text: "gyro_stability_score: " + s(detailObj.gyro_stability_score) }
                Label { text: "signal_quality_baseline: " + s(detailObj.signal_quality_baseline) }
                Label { text: "failure_reason: " + s(detailObj.failure_reason) }
                Label { text: "Full Calibration Detail"; font.bold: true }
                TextArea {
                    width: Math.max(320, parent.width - 20)
                    height: Math.min(520, Math.max(320, contentHeight + 36))
                    readOnly: true
                    selectByMouse: true
                    text: root.detailText
                    wrapMode: Text.WordWrap
                }
            }
        }

        GroupBox {
            title: "Calibration Action Result"
            Column {
                spacing: 3
                Label { text: "action: " + s(lastActionObj.action_id || selectedCommandId) }
                Label { text: "status: " + s(lastActionObj.status || selectedStatus) }
                Label { text: "message: " + s(lastActionObj.message || lastActionObj.reason) }
                Label { text: "result: " + s(lastActionObj.result) }
            }
        }

        GroupBox {
            title: "Calibration Progress"
            visible: activePanel === "progress" || calibrationRunning
            Column {
                spacing: 4
                Label { text: "calibration_progress_status: " + s(calibrationProgressStatus); font.bold: true }
                Label { text: "current_phase: " + s(calibrationProgressPhase) }
                Label { text: "output_count: " + String(calibrationOutputCount) }
                Label { text: "start_command: " + s(calibrationStartCommand); wrapMode: Text.WordWrap }
                Label {
                    text: "Full phase prompts and CLI output are shown here so the operator can confirm the calibration workflow and stage."
                    wrapMode: Text.WordWrap
                }
                TextArea {
                    width: Math.max(320, parent.width - 20)
                    height: Math.min(560, Math.max(360, contentHeight + 36))
                    readOnly: true
                    selectByMouse: true
                    text: calibrationProgressText
                    wrapMode: Text.WordWrap
                }
                Flow {
                    width: parent.width
                    spacing: 6
                    DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Refresh Calibration Progress"; onClicked: root.doPollProgress() }
                    DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Latest Calibration"; onClicked: root.doLatest() }
                    DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "List Calibrations"; onClicked: root.doList() }
                }
            }
        }


        GroupBox {
            title: "Calibration Modes"
            Column {
                Label { text: "First Profile Calibration" }
                Label { text: "Quick Check" }
                Label { text: "Periodic Recalibration" }
                Label { text: "Triggered Recalibration" }
                Label { text: "GUI now displays Calibration Progress; full IPC start uses the existing calibration CLI command path."; wrapMode: Text.WordWrap }
            }
        }

        GroupBox {
            title: "Page Commands"
            Label { text: commandSummary; wrapMode: Text.WordWrap }
        }

        PageFeedbackPanel {
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            feedbackStyleObj: root.componentStyleObj.feedback_panel || ({})
            pageId: "calibration"
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
