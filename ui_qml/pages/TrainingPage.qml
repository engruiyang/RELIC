import QtQuick
import QtQuick.Controls
import "../components"

Item {
    property var appStateObj: ({})
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property var gameHudObj: ({})
    property string commandSummary: ""
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""

    property string activePanel: "readiness"
    property var profileResult: ({})
    property var calibrationResult: ({})
    property var sessionResult: ({})
    property var gameResult: ({})
    property var actionResult: ({})
    property string actionResultText: "No training action yet."
    property string readinessReason: "refresh_required"

    signal invokeNative(string actionId)

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    function parseJson(text) {
        try {
            return JSON.parse(text || "{}")
        } catch (e) {
            return ({
                "action_id": "parse_error",
                "status": "parse_error",
                "message": String(e)
            })
        }
    }

    function currentUserId() {
        var uid = controlStateObj.current_user_id
        if (uid === undefined || uid === null || uid === "" || uid === "n/a") {
            uid = appStateObj.current_user_id
        }
        return (uid === undefined || uid === null) ? "" : String(uid)
    }

    function profileDetail() {
        if (profileResult.detail !== undefined && profileResult.detail !== null) {
            return profileResult.detail
        }
        if (profileResult.profile !== undefined && profileResult.profile !== null) {
            return profileResult.profile
        }
        return ({})
    }

    function calibrationDetail() {
        if (calibrationResult.calibration !== undefined && calibrationResult.calibration !== null) {
            return calibrationResult.calibration
        }
        if (calibrationResult.detail !== undefined && calibrationResult.detail !== null) {
            return calibrationResult.detail
        }
        return ({})
    }

    function profileLoaded() {
        var p = profileDetail()
        if (p.profile_loaded === true || p.profile_loaded === "true") {
            return true
        }
        if (profileResult.status === "accepted" || profileResult.status === "user_loaded") {
            return true
        }
        return controlStateObj.profile_loaded === true || controlStateObj.profile_loaded === "true"
    }

    function calibrationUsable() {
        var c = calibrationDetail()
        if (c.calibration_usable === true || c.calibration_usable === "true") {
            return true
        }
        if (c.latest_valid === true || c.latest_valid === "true") {
            return true
        }
        return controlStateObj.calibration_usable === true || controlStateObj.calibration_usable === "true"
    }

    function lastCalibrationId() {
        var c = calibrationDetail()
        if (c.last_calibration_id !== undefined && c.last_calibration_id !== null && c.last_calibration_id !== "") {
            return String(c.last_calibration_id)
        }
        var p = profileDetail()
        if (p.last_calibration_id !== undefined && p.last_calibration_id !== null && p.last_calibration_id !== "") {
            return String(p.last_calibration_id)
        }
        return s(controlStateObj.last_calibration_id)
    }

    function computeReadinessReason() {
        if (currentUserId() === "") {
            return "no_user"
        }
        if (!profileLoaded()) {
            return "profile_not_loaded"
        }
        if (lastCalibrationId() === "n/a" || lastCalibrationId() === "None") {
            return "no_calibration"
        }
        if (!calibrationUsable()) {
            return "calibration_not_usable"
        }
        return "ready"
    }

    function formalTrainingAllowed() {
        return computeReadinessReason() === "ready"
    }

    function resultSummary(obj) {
        var lines = []
        lines.push("action: " + s(obj.action_id))
        lines.push("status: " + s(obj.status))
        lines.push("message: " + s(obj.message))
        lines.push("result: " + s(obj.result))
        lines.push("accepted: " + s(obj.accepted))
        return lines.join("\n")
    }

    function callAction(actionId, payload) {
        var raw = ""
        if (typeof guiBridge === "undefined" || !guiBridge) {
            return ({
                "action_id": actionId,
                "status": "bridge_missing",
                "message": "guiBridge unavailable",
                "accepted": false
            })
        }
        raw = guiBridge.invokeAction(actionId, JSON.stringify(payload || {}))
        return parseJson(raw)
    }

    function setActionResult(obj, panelName) {
        actionResult = obj || ({})
        selectedCommandId = s(actionResult.action_id)
        selectedStatus = s(actionResult.status)
        selectedExecutionMode = "native"
        selectedNativeActionId = s(actionResult.action_id)
        actionResultText = resultSummary(actionResult)
        if (panelName !== undefined && panelName !== "") {
            activePanel = panelName
        }
    }

    function refreshReadiness() {
        var uid = currentUserId()
        if (uid === "") {
            var missing = {
                "action_id": "training.readiness",
                "status": "missing_user",
                "message": "No current user loaded. Load or create a user first.",
                "accepted": false
            }
            readinessReason = "no_user"
            setActionResult(missing, "readiness")
            return
        }
        profileResult = callAction("user.show_profile", {"user_id": uid})
        calibrationResult = callAction("calibration.status", {"user_id": uid})
        readinessReason = computeReadinessReason()
        setActionResult({
            "action_id": "training.readiness",
            "status": readinessReason === "ready" ? "ready" : "not_ready",
            "message": readinessReason,
            "result": "readiness_checked",
            "accepted": readinessReason === "ready"
        }, "readiness")
    }

    function startTrainingSession() {
        refreshReadiness()
        if (!formalTrainingAllowed()) {
            setActionResult({
                "action_id": "session.start",
                "status": "training_not_ready",
                "message": "Start blocked: " + readinessReason,
                "result": "blocked_by_readiness_gate",
                "accepted": false
            }, "result")
            return
        }
        sessionResult = callAction("session.start", {"user_id": currentUserId()})
        setActionResult(sessionResult, "session")
    }

    function stopTrainingSession() {
        sessionResult = callAction("session.stop", {})
        setActionResult(sessionResult, "session")
    }

    function querySessionStatus() {
        sessionResult = callAction("session.status", {})
        setActionResult(sessionResult, "session")
    }

    function queryGameStatus() {
        gameResult = callAction("game.status", {})
        setActionResult(gameResult, "game")
    }

    function safeStop() {
        sessionResult = callAction("live.safe_stop", {})
        setActionResult(sessionResult, "session")
    }

    ScrollView {
        anchors.fill: parent
        clip: true

        Column {
            width: parent.width
            spacing: 8

            PageHeader {
                titleText: "Training Page"
                subtitleText: "Training readiness gate + existing session/game commands"
            }

            GroupBox {
                title: "Training Readiness"
                width: parent.width
                Column {
                    width: parent.width
                    spacing: 4
                    Label { text: "current_user_id: " + s(currentUserId()) }
                    Label { text: "profile_loaded: " + s(profileLoaded()) }
                    Label { text: "last_calibration_id: " + s(lastCalibrationId()) }
                    Label { text: "calibration_usable: " + s(calibrationUsable()) }
                    Label { text: "formal_training_allowed: " + s(formalTrainingAllowed()) }
                    Label { text: "readiness_reason: " + s(computeReadinessReason()) }
                    Label {
                        text: formalTrainingAllowed() ? "Ready for formal training." : "Formal training is not ready. Resolve user/calibration prerequisites first."
                        wrapMode: Text.WordWrap
                    }
                }
            }

            GroupBox {
                title: "Training Page Actions"
                width: parent.width
                Flow {
                    width: parent.width
                    spacing: 6
                    Button {
                        text: "Refresh Readiness"
                        onClicked: refreshReadiness()
                    }
                    Button {
                        text: "Start Session"
                        onClicked: startTrainingSession()
                    }
                    Button {
                        text: "Stop Session"
                        onClicked: stopTrainingSession()
                    }
                    Button {
                        text: "Safe Stop"
                        onClicked: safeStop()
                    }
                    Button {
                        text: "Session Status"
                        onClicked: querySessionStatus()
                    }
                    Button {
                        text: "Game Status"
                        onClicked: queryGameStatus()
                    }
                }
            }

            GroupBox {
                title: "Session Status"
                width: parent.width
                visible: activePanel === "session" || activePanel === "readiness" || activePanel === "result"
                Column {
                    width: parent.width
                    spacing: 4
                    Label { text: "session_active: " + s(controlStateObj.session_active) }
                    Label { text: "current_session_id: " + s(controlStateObj.current_session_id) }
                    Label { text: "session_elapsed_ms: " + s(controlStateObj.session_elapsed_ms) }
                    Label { text: "latest_report_path: " + s(controlStateObj.latest_report_path) }
                    Label { text: "last_session_status: " + s(controlStateObj.last_session_status) }
                    Label { text: "session.action_status: " + s(sessionResult.status) }
                    Label { text: "session.message: " + s(sessionResult.message); wrapMode: Text.WordWrap }
                }
            }

            GroupBox {
                title: "Runtime Signal Summary"
                width: parent.width
                visible: activePanel === "readiness" || activePanel === "session"
                Column {
                    width: parent.width
                    spacing: 4
                    Label { text: "quality_state: " + s(runtimeObj.quality_state) }
                    Label { text: "control_state: " + s(runtimeObj.control_state) }
                    Label { text: "fi_smoothed: " + s(runtimeObj.fi_smoothed) }
                    Label { text: "attention: " + s(runtimeObj.attention) }
                    Label { text: "attention_fresh: " + s(runtimeObj.attention_fresh) }
                    Label { text: "attention_age_ms: " + s(runtimeObj.attention_age_ms) }
                    Label { text: "gyro_fresh: " + s(runtimeObj.gyro_fresh) }
                    Label { text: "gyro_age_ms: " + s(runtimeObj.gyro_age_ms) }
                    Label { text: "warning_flags: " + s(runtimeObj.warning_flags) }
                    Label { text: "error_flags: " + s(runtimeObj.error_flags) }
                }
            }

            GroupBox {
                title: "Game HUD Summary"
                width: parent.width
                visible: activePanel === "game" || activePanel === "session" || activePanel === "readiness"
                Column {
                    width: parent.width
                    spacing: 4
                    Label { text: "game_id: " + s(gameHudObj.game_id) }
                    Label { text: "score: " + s(gameHudObj.score) }
                    Label { text: "combo: " + s(gameHudObj.combo) }
                    Label { text: "level: " + s(gameHudObj.level) }
                    Label { text: "behavior_sample_count: " + s(controlStateObj.behavior_sample_count) }
                    Label { text: "score_update_count: " + s(gameHudObj.score_update_count) }
                    Label { text: "feedback_hint: " + s(gameHudObj.feedback_hint) }
                    Label { text: "game.action_status: " + s(gameResult.status) }
                }
            }

            GroupBox {
                title: "GameCanvas Placeholder"
                width: parent.width
                Column {
                    spacing: 4
                    Label { text: "GameCanvas will be restored in TASK24" }
                    Label { text: "Fragment Lock / 碎片锁定: reference ready" }
                    Label { text: "Signal Hunter / 信号猎手: planned" }
                    Label { text: "Stabilizer / 稳定协议: planned" }
                }
            }

            GroupBox {
                title: "Training Action Result"
                width: parent.width
                TextArea {
                    width: parent.width
                    height: Math.min(260, Math.max(120, contentHeight + 36))
                    readOnly: true
                    wrapMode: TextArea.Wrap
                    text: actionResultText
                }
            }

            GroupBox {
                title: "Page Commands"
                width: parent.width
                Label {
                    width: parent.width
                    text: commandSummary
                    wrapMode: Text.WordWrap
                }
            }

            PageFeedbackPanel {
                pageId: "training"
                selectedCommandId: selectedCommandId
                selectedStatus: selectedStatus
                selectedExecutionMode: selectedExecutionMode
                selectedNativeActionId: selectedNativeActionId
                lastCommand: s(controlStateObj.last_command)
                lastResult: s(controlStateObj.last_command_result)
                lastError: s(controlStateObj.last_command_error)
            }
        }
    }

    Component.onCompleted: {
        readinessReason = computeReadinessReason()
    }
}

// Page Feedback
