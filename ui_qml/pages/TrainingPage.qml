import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: trainingPage

    property var appStateObj: ({})
    property var controlStateObj: ({})
    property var runtimeObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})
    property string commandSummary: ""
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""

    property string activePanel: "readiness"
    property var availableGameIds: ["trace_lock"]
    property string selectedGameId: "trace_lock"
    property var gameSelectResult: ({})
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

    function currentGameView() {
        if (gameViewObj !== undefined && gameViewObj !== null) {
            return gameViewObj
        }
        return ({})
    }

    function gameEntities() {
        var gv = currentGameView()
        return (gv.entities && Array.isArray(gv.entities)) ? gv.entities : []
    }

    function gameVisualEvents() {
        var gv = currentGameView()
        return (gv.visual_events && Array.isArray(gv.visual_events)) ? gv.visual_events : []
    }

    function gameViewField(key) {
        var gv = currentGameView()
        if (gv[key] !== undefined && gv[key] !== null && gv[key] !== "") {
            return gv[key]
        }
        if (gameHudObj[key] !== undefined && gameHudObj[key] !== null && gameHudObj[key] !== "") {
            return gameHudObj[key]
        }
        return "n/a"
    }

    function hasActiveGameView() {
        var gv = currentGameView()
        return gameEntities().length > 0 || gameVisualEvents().length > 0 || s(gv.game_id) !== "n/a"
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
        if (selectedGameId !== "") {
            gameSelectResult = callAction("game.select", {"game_id": selectedGameId})
            if (!(gameSelectResult.accepted === true || gameSelectResult.status === "accepted")) {
                setActionResult({
                    "action_id": "session.start",
                    "status": "game_select_failed",
                    "message": "Start blocked: game.select failed for " + selectedGameId,
                    "result": gameSelectResult,
                    "accepted": false
                }, "game")
                return
            }
        }
        sessionResult = callAction("session.start", {"user_id": currentUserId(), "game_id": selectedGameId})
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

    function selectExistingGame() {
        gameSelectResult = callAction("game.select", {"game_id": selectedGameId})
        gameResult = gameSelectResult
        setActionResult(gameSelectResult, "game")
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
                title: "Game Selection"
                width: parent.width

                Column {
                    width: parent.width
                    spacing: 6

                    Label { text: "Select Existing Game" }
                    Label { text: "selected_game_id: " + s(selectedGameId) }
                    Label { text: "current_game_id: " + s(gameViewField("game_id")) }
                    Label {
                        width: parent.width
                        text: "Only existing TraceLock is exposed here; GUI does not create a new game pipeline."
                        wrapMode: Text.WordWrap
                    }

                    Row {
                        width: parent.width
                        spacing: 8

                        ComboBox {
                            id: trainingGameSelector
                            width: Math.min(parent.width - 180, 360)
                            model: trainingPage.availableGameIds
                            currentIndex: Math.max(0, trainingPage.availableGameIds.indexOf(trainingPage.selectedGameId))
                            onActivated: function(index) {
                                if (index >= 0 && index < trainingPage.availableGameIds.length) {
                                    trainingPage.selectedGameId = trainingPage.availableGameIds[index]
                                }
                            }
                        }

                        Button {
                            text: "Use TraceLock"
                            onClicked: {
                                trainingPage.selectedGameId = "trace_lock"
                                trainingPage.selectExistingGame()
                            }
                        }
                    }

                    Label { text: "game.select status: " + s(gameSelectResult.status) }
                    Label { text: "game.select message: " + s(gameSelectResult.message); wrapMode: Text.WordWrap }
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
                    Label { text: "max_combo: " + s(gameHudObj.max_combo) }
                    Label { text: "movement_type: " + s(gameHudObj.movement_type) }
                    Label { text: "target_time_left_ms: " + s(gameHudObj.target_time_left_ms) }
                    Label { text: "target_lifetime_ms: " + s(gameHudObj.target_lifetime_ms) }
                    Label { text: "accuracy: " + s(gameHudObj.accuracy) }
                    Label { text: "omission: " + s(gameHudObj.omission) }
                    Label { text: "false_action: " + s(gameHudObj.false_action) }
                    Label { text: "rt_stability: " + s(gameHudObj.rt_stability) }
                    Label { text: "behavior_sample_count: " + s(controlStateObj.behavior_sample_count) }
                    Label { text: "score_update_count: " + s(gameHudObj.score_update_count) }
                    Label { text: "feedback_hint: " + s(gameHudObj.feedback_hint) }
                    Label { text: "game.action_status: " + s(gameResult.status) }
                }
            }

            GroupBox {
                title: "GameCanvas / Game View"
                width: parent.width

                Column {
                    width: parent.width
                    spacing: 6

                    Label { text: "GameCanvas restored in TASK24" }
                    Label { text: "GameCanvas will be restored in TASK24" }
                    Label { text: hasActiveGameView() ? "Game view active." : "No active game view." }

                    Row {
                        width: parent.width
                        spacing: 12
                        Label { text: "game_id: " + s(gameViewField("game_id")) }
                        Label { text: "score: " + s(gameViewField("score")) }
                        Label { text: "combo: " + s(gameViewField("combo")) }
                        Label { text: "level: " + s(gameViewField("level")) }
                        Label { text: "entity_count: " + s(gameEntities().length) }
                        Label { text: "visual_event_count: " + s(gameVisualEvents().length) }
                    }

                    GameCanvas {
                        id: trainingGameCanvas
                        width: parent.width
                        height: 360
                        gameView: trainingPage.currentGameView()
                        guiBridgeRef: (typeof guiBridge !== "undefined") ? guiBridge : null
                        fallbackGameId: s(gameViewField("game_id"))
                    }

                    Label {
                        width: parent.width
                        text: "Pointer input is routed through guiBridge.sendEvent('pointer_click', ...); hit testing remains in the existing game client / TraceLock pipeline."
                        wrapMode: Text.WordWrap
                    }

                    Label { text: "TraceLock / Fragment Lock / 碎片锁定: existing game client active" }
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
