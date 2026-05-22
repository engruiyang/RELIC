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
    property var renderResourcesObj: ({})
    property var designThemeObj: ({})
    property var pageStyleObj: ({})
    property var componentStyleObj: ({})
    property var gameStyleObj: ({})
    property var effectStyleObj: ({})
    property string commandSummary: ""
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""

    property string activePanel: "readiness"
    property var availableGameIds: ["trace_lock"]
    property string selectedGameId: "trace_lock"
    property var difficultyModes: ["auto", "manual"]
    property string selectedDifficultyMode: "auto"
    property var difficultyLevels: [1, 2, 3, 4, 5]
    property int selectedDifficultyLevel: 3
    property var gameSelectResult: ({})
    property var difficultyResult: ({})
    property var profileResult: ({})
    property var calibrationResult: ({})
    property var sessionResult: ({})
    property var gameResult: ({})
    property var actionResult: ({})
    property string actionResultText: "No training action yet."
    property string readinessReason: "refresh_required"
    property string lastDifficultyButtonFeedback: "No difficulty action yet."
    property int difficultyActionSerial: 0
    property string difficultyButtonState: "idle"

    signal invokeNative(string actionId)

    function s(v) {
        return (v === undefined || v === null || v === "") ? "n/a" : String(v)
    }

    function objectValue(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function themeColor(key, fallbackValue) {
        return objectValue(designThemeObj.colors || ({}), key, fallbackValue)
    }

    function themeSpacing(key, fallbackValue) {
        return Number(objectValue(designThemeObj.spacing || ({}), key, fallbackValue))
    }

    function componentStyle(componentId) {
        return objectValue(componentStyleObj, componentId, ({}))
    }

    function panelValue(key, fallbackValue) {
        return objectValue(componentStyle("panel"), key, fallbackValue)
    }

    function gameDesignValue(section, key, fallbackValue) {
        var sectionObj = objectValue(gameStyleObj, section, ({}))
        return objectValue(sectionObj, key, fallbackValue)
    }

    function gameHudCardStyle() {
        var hud = gameStyleObj.hud || ({})
        return ({
            "background": objectValue(hud, "metric_card_background", themeColor("panel", "#0F172A")),
            "border": objectValue(hud, "metric_card_border", themeColor("panel_border", "#334155")),
            "width": Number(objectValue(hud, "metric_width", (pageStyleObj.layout || ({})).hud_metric_width || 170)),
            "height": Number(objectValue(hud, "metric_height", (pageStyleObj.layout || ({})).hud_metric_height || 92)),
            "label_size": Number(objectValue(hud, "metric_title_size", 12)),
            "value_size": Number(objectValue(hud, "metric_value_size", 24)),
            "value_color": objectValue(hud, "text_color", themeColor("accent", "#22D3EE")),
            "label_color": themeColor("text_muted", "#94A3B8"),
            "padding": 10,
            "radius": 10
        })
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

    function difficultyStartPayload() {
        return {
            "difficulty_mode": selectedDifficultyMode,
            "difficulty_level": selectedDifficultyMode === "manual" ? selectedDifficultyLevel : null,
            "debug_difficulty": selectedDifficultyMode === "manual" ? selectedDifficultyLevel : "auto",
            "selected_difficulty_level": selectedDifficultyMode === "manual" ? selectedDifficultyLevel : "auto"
        }
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

        // TASK24C-3: session.start carries the selected difficulty as a reliable
        // backend sync path. Apply/Reset buttons remain available, but starting a
        // session no longer depends on a separate difficulty button click.
        var payload = {
            "user_id": currentUserId(),
            "game_id": selectedGameId,
            "difficulty_mode": selectedDifficultyMode,
            "difficulty_level": selectedDifficultyMode === "manual" ? selectedDifficultyLevel : null,
            "debug_difficulty": selectedDifficultyMode === "manual" ? selectedDifficultyLevel : "auto",
            "selected_difficulty_level": selectedDifficultyMode === "manual" ? selectedDifficultyLevel : "auto"
        }
        updateDifficultyFeedback("session.start will sync difficulty mode="
                                 + selectedDifficultyMode
                                 + " level="
                                 + s(payload.selected_difficulty_level))
        sessionResult = callAction("session.start", payload)
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

    function updateDifficultyFeedback(message) {
        difficultyActionSerial += 1
        lastDifficultyButtonFeedback = "#" + difficultyActionSerial + " " + message
    }

    function dispatchDifficulty(mode, level, label) {
        var payload = {
            "game_id": selectedGameId,
            "mode": mode,
            "level": mode === "manual" ? level : null
        }
        difficultyButtonState = "dispatching"
        updateDifficultyFeedback(label + " pressed; dispatching game.difficulty")

        if (selectedGameId !== "trace_lock") {
            selectedGameId = "trace_lock"
        }
        if (s(gameViewField("game_id")) !== "trace_lock") {
            gameSelectResult = callAction("game.select", {"game_id": "trace_lock"})
        }

        difficultyResult = callAction("game.difficulty", payload)

        if (difficultyResult.status === "unsupported"
                || difficultyResult.status === "not_implemented"
                || difficultyResult.status === "unsupported_game"
                || difficultyResult.status === "bridge_missing") {
            if (typeof guiBridge !== "undefined" && guiBridge) {
                guiBridge.sendCommand("set_debug_difficulty", JSON.stringify({"level": mode === "manual" ? level : null}))
                difficultyResult = {
                    "action_id": "game.difficulty",
                    "status": "sent_via_legacy_command",
                    "message": "fallback set_debug_difficulty command sent",
                    "accepted": true,
                    "difficulty_mode": mode,
                    "debug_difficulty": mode === "manual" ? level : "auto",
                    "level": mode === "manual" ? level : "auto"
                }
            }
        }

        gameResult = difficultyResult
        difficultyButtonState = s(difficultyResult.status)
        updateDifficultyFeedback(label + " result=" + s(difficultyResult.status)
                                 + " mode=" + mode
                                 + " debug=" + s(difficultyResult.debug_difficulty)
                                 + " level=" + s(difficultyResult.level))
        setActionResult(difficultyResult, "game")
    }

    function applyTraceLockDifficulty() {
        var mode = selectedDifficultyMode === "auto" ? "auto" : "manual"
        var level = mode === "manual" ? selectedDifficultyLevel : null
        var label = mode === "auto"
                ? "Apply Difficulty auto"
                : "Apply Difficulty manual level " + selectedDifficultyLevel
        dispatchDifficulty(mode, level, label)
    }

    function resetTraceLockAutoDifficulty() {
        selectedDifficultyMode = "auto"
        dispatchDifficulty("auto", null, "Reset Auto Difficulty")
    }

    function difficultyValue(key) {
        if (difficultyResult[key] !== undefined && difficultyResult[key] !== null && difficultyResult[key] !== "") {
            return difficultyResult[key]
        }
        return gameViewField(key)
    }

    function safeStop() {
        sessionResult = callAction("live.safe_stop", {})
        setActionResult(sessionResult, "session")
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: trainingPage.designThemeObj
        styleObj: trainingPage.pageStyleObj
        renderResourcesObj: trainingPage.renderResourcesObj
        fallbackColor: (trainingPage.designThemeObj.colors && trainingPage.designThemeObj.colors.background) ? trainingPage.designThemeObj.colors.background : "#F8FAFC"
    }

    ScrollView {
        anchors.fill: parent
        anchors.margins: Number((pageStyleObj.layout || ({})).content_margin || themeSpacing("page_margin", 0))
        clip: true

        Column {
            width: parent.width
            spacing: Number((pageStyleObj.layout || ({})).section_spacing || themeSpacing("section_gap", 8))

            PageHeader {
            renderResourcesObj: trainingPage.renderResourcesObj
            designThemeObj: trainingPage.designThemeObj
            componentStyleObj: trainingPage.componentStyleObj
            headerStyleObj: trainingPage.componentStyleObj.header || ({})
                titleText: "Training Page"
                subtitleText: "Training readiness gate + existing session/game commands"
            }

            GroupBox {
                title: "Design Pack Status"
                width: parent.width
                Column {
                    width: parent.width
                    spacing: 4
                    Label { text: "design_pack: " + s(objectValue(renderResourcesObj.design_pack || ({}), "pack_id", "default")) }
                    Label { text: "game_styles: " + s(objectValue(gameStyleObj, "game_id", "trace_lock")) }
                    Label { text: "effect_styles: " + s(Object.keys(effectStyleObj || ({})).join(",")) }
                    Label { text: "panel_token_background: " + s(panelValue("background", "fallback")) }
                }
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
                    DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
                        text: "Refresh Readiness"
                        onClicked: refreshReadiness()
                    }
                    DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
                        text: "Start Session"
                        onClicked: startTrainingSession()
                    }
                    DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
                        text: "Stop Session"
                        onClicked: stopTrainingSession()
                    }
                    DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
                        text: "Safe Stop"
                        onClicked: safeStop()
                    }
                    DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
                        text: "Session Status"
                        onClicked: querySessionStatus()
                    }
                    DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
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

                        DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
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
                title: "TraceLock Difficulty"
                width: parent.width

                Column {
                    width: parent.width
                    spacing: 6

                    Label { text: "Difficulty Control" }
                    Label { text: "difficulty_mode: " + s(difficultyValue("difficulty_mode")) }
                    Label { text: "debug_difficulty: " + s(difficultyValue("debug_difficulty")) }
                    Label { text: "effective_level: " + s(difficultyValue("effective_level")) }
                    Label { text: "dynamic_difficulty_enabled: " + s(difficultyValue("dynamic_difficulty_enabled")) }
                    Label { text: "selected_difficulty_level: " + s(selectedDifficultyLevel) }
                    Label {
                        width: parent.width
                        text: "Manual locks TraceLock at the selected level. Auto enables TraceLock DDA and may adjust level during play."
                        wrapMode: Text.WordWrap
                    }
                    Label { text: "difficulty_button_state: " + s(difficultyButtonState) }
                    Label {
                        width: parent.width
                        text: "last difficulty button: " + s(lastDifficultyButtonFeedback)
                        wrapMode: Text.WordWrap
                    }
                    Label {
                        width: parent.width
                        text: "Button feedback is text-based to stay compatible with the native Qt Quick Controls style."
                        wrapMode: Text.WordWrap
                    }

                    Row {
                        width: parent.width
                        spacing: 8

                        ComboBox {
                            id: difficultyModeSelector
                            width: 160
                            model: trainingPage.difficultyModes
                            currentIndex: Math.max(0, trainingPage.difficultyModes.indexOf(trainingPage.selectedDifficultyMode))
                            onActivated: function(index) {
                                if (index >= 0 && index < trainingPage.difficultyModes.length) {
                                    trainingPage.selectedDifficultyMode = trainingPage.difficultyModes[index]
                                }
                            }
                        }

                        ComboBox {
                            id: difficultyLevelSelector
                            width: 120
                            model: trainingPage.difficultyLevels
                            enabled: trainingPage.selectedDifficultyMode === "manual"
                            currentIndex: Math.max(0, trainingPage.difficultyLevels.indexOf(trainingPage.selectedDifficultyLevel))
                            onActivated: function(index) {
                                if (index >= 0 && index < trainingPage.difficultyLevels.length) {
                                    trainingPage.selectedDifficultyLevel = trainingPage.difficultyLevels[index]
                                }
                            }
                        }

                        DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
                            id: applyDifficultyButton
                            text: applyDifficultyButton.down ? "Applying..." : "Apply Difficulty"
                            onPressed: trainingPage.updateDifficultyFeedback("Apply Difficulty pressed visually")
                            onClicked: trainingPage.applyTraceLockDifficulty()
                        }

                        DesignButton { buttonStyleObj: trainingPage.componentStyleObj.button || ({}); themeObj: trainingPage.designThemeObj; renderResourcesObj: trainingPage.renderResourcesObj;
                            id: resetAutoDifficultyButton
                            text: resetAutoDifficultyButton.down ? "Resetting..." : "Reset Auto Difficulty"
                            onPressed: trainingPage.updateDifficultyFeedback("Reset Auto Difficulty pressed visually")
                            onClicked: trainingPage.resetTraceLockAutoDifficulty()
                        }
                    }

                    Label { text: "game.difficulty status: " + s(difficultyResult.status) }
                    Label { text: "game.difficulty message: " + s(difficultyResult.message); wrapMode: Text.WordWrap }
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
                    spacing: 8

                    Flow {
                        width: parent.width
                        spacing: 8

                        DesignMetricCard { label: "Score"; value: s(gameHudObj.score); themeObj: trainingPage.designThemeObj; cardStyleObj: trainingPage.gameHudCardStyle() }
                        DesignMetricCard { label: "Combo"; value: s(gameHudObj.combo) + " / " + s(gameHudObj.max_combo); themeObj: trainingPage.designThemeObj; cardStyleObj: trainingPage.gameHudCardStyle() }
                        DesignMetricCard { label: "Level"; value: s(gameHudObj.effective_level || gameHudObj.level); themeObj: trainingPage.designThemeObj; cardStyleObj: trainingPage.gameHudCardStyle() }
                        DesignMetricCard { label: "Difficulty"; value: s(gameHudObj.difficulty_mode) + " / " + s(gameHudObj.debug_difficulty); themeObj: trainingPage.designThemeObj; cardStyleObj: trainingPage.gameHudCardStyle() }
                        DesignMetricCard { label: "Accuracy"; value: s(gameHudObj.accuracy); themeObj: trainingPage.designThemeObj; cardStyleObj: trainingPage.gameHudCardStyle() }
                        DesignMetricCard { label: "Omission"; value: s(gameHudObj.omission); themeObj: trainingPage.designThemeObj; cardStyleObj: trainingPage.gameHudCardStyle() }
                        DesignMetricCard { label: "False Action"; value: s(gameHudObj.false_action); themeObj: trainingPage.designThemeObj; cardStyleObj: trainingPage.gameHudCardStyle() }
                        DesignMetricCard { label: "Time Left"; value: s(gameHudObj.time_left_ms); themeObj: trainingPage.designThemeObj; cardStyleObj: trainingPage.gameHudCardStyle() }
                    }

                    Label { text: "game_id: " + s(gameHudObj.game_id) }
                    Label { text: "movement_type: " + s(gameHudObj.movement_type) }
                    Label { text: "target_time_left_ms: " + s(gameHudObj.target_time_left_ms) }
                    Label { text: "target_lifetime_ms: " + s(gameHudObj.target_lifetime_ms) }
                    Label { text: "target_pressure_level: " + s(gameHudObj.target_pressure_level) }
                    Label { text: "dynamic_difficulty_enabled: " + s(gameHudObj.dynamic_difficulty_enabled) }
                    Label { text: "difficulty_locked: " + s(gameHudObj.difficulty_locked) }
                    Label { text: "selected_difficulty_level: " + s(selectedDifficultyLevel) }
                    Label { text: "elapsed_ms: " + s(gameHudObj.elapsed_ms) }
                    Label { text: "game_duration_ms: " + s(gameHudObj.game_duration_ms) }
                    Label { text: "game_completed: " + s(gameHudObj.game_completed) }
                    Label { text: "rt_stability: " + s(gameHudObj.rt_stability) }
                    Label { text: "behavior_sample_count: " + s(controlStateObj.behavior_sample_count) }
                    Label { text: "score_update_count: " + s(gameHudObj.score_update_count) }
                    Label { text: "feedback_hint: " + s(gameHudObj.feedback_hint) }
                    Label { text: "game.action_status: " + s(gameResult.status) }
                    Label { text: "TASK25B enlarged design-pack HUD metric cards active" }
                }
            }

            GroupBox {
                title: "GameCanvas / Game View"
                width: parent.width

                Column {
                    width: parent.width
                    spacing: 6

                    Label { text: "GameCanvas restored in TASK24" }
                    Label { text: "TASK25 design_pack game_styles active" }
                    Label { text: "GameCanvas will be restored in TASK24" }
                    Label { text: hasActiveGameView() ? "Game view active." : "No active game view." }

                    Row {
                        width: parent.width
                        spacing: 12
                        Label { text: "game_id: " + s(gameViewField("game_id")) }
                        Label { text: "score: " + s(gameViewField("score")) }
                        Label { text: "combo: " + s(gameViewField("combo")) }
                        Label { text: "level: " + s(gameViewField("level")) }
                        Label { text: "time_left_ms: " + s(gameViewField("time_left_ms")) }
                        Label { text: "entity_count: " + s(gameEntities().length) }
                        Label { text: "visual_event_count: " + s(gameVisualEvents().length) }
                    }

                    GameCanvas {
                        id: trainingGameCanvas
                        width: parent.width
                        height: Number(gameDesignValue("canvas", "height", 360))
                        gameView: trainingPage.currentGameView()
                        guiBridgeRef: (typeof guiBridge !== "undefined") ? guiBridge : null
                        fallbackGameId: s(gameViewField("game_id"))
                        designThemeObj: trainingPage.designThemeObj
                        gameStyleObj: trainingPage.gameStyleObj
                        effectStyleObj: trainingPage.effectStyleObj
                        renderResourcesObj: trainingPage.renderResourcesObj
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
            renderResourcesObj: trainingPage.renderResourcesObj
            designThemeObj: trainingPage.designThemeObj
            componentStyleObj: trainingPage.componentStyleObj
            feedbackStyleObj: trainingPage.componentStyleObj.feedback_panel || ({})
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
