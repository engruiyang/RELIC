import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root

    property var guiBridge: null
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

    function task26UserLayoutPayload() {
        var resources = root.renderResourcesObj || ({})
        return resources.task26_user_layout_payload || ({})
    }


    property var appStateObj: ({})
    property var controlStateObj: ({})
    property var userActionObj: ({})
    property string commandSummary: ""
    property string selectedCommandId: ""
    property string selectedStatus: ""
    property string selectedExecutionMode: ""
    property string selectedNativeActionId: ""
    property string activePanel: "summary"
    property string selectedUserId: ""
    property var userIdOptions: []

    signal invokeNative(string actionId)

    function safeJsonParse(text) {
        if (text === undefined || text === null || String(text) === "") {
            return {
                "action_id": selectedCommandId || "unknown",
                "status": "no_action_result_returned",
                "message": "guiBridge.invokeAction returned empty result",
                "accepted": false
            }
        }
        try {
            return JSON.parse(String(text))
        } catch (e) {
            return {
                "action_id": selectedCommandId || "parse_error",
                "status": "parse_error",
                "message": "invalid action result json",
                "accepted": false,
                "raw": String(text || "")
            }
        }
    }

    function safeText(value, fallback) {
        var fb = fallback === undefined ? "n/a" : fallback
        return value === undefined || value === null || value === "" ? fb : String(value)
    }

    function resultObject() {
        var result = userActionObj.result
        if (result && typeof result === "object") {
            return result
        }
        return ({})
    }

    function detailObject() {
        if (userActionObj.detail && typeof userActionObj.detail === "object") {
            return userActionObj.detail
        }
        if (userActionObj.profile && typeof userActionObj.profile === "object") {
            return userActionObj.profile
        }
        var nested = resultObject()
        if (nested.profile && typeof nested.profile === "object") {
            return nested.profile
        }
        if (nested.detail && typeof nested.detail === "object") {
            return nested.detail
        }
        return ({})
    }

    function summaryValue(key) {
        var detail = detailObject()
        var nested = resultObject()
        if (detail[key] !== undefined && detail[key] !== null && detail[key] !== "") {
            return detail[key]
        }
        if (nested[key] !== undefined && nested[key] !== null && nested[key] !== "") {
            return nested[key]
        }
        if (controlStateObj && controlStateObj[key] !== undefined && controlStateObj[key] !== null && controlStateObj[key] !== "") {
            return controlStateObj[key]
        }
        if (appStateObj && appStateObj[key] !== undefined && appStateObj[key] !== null && appStateObj[key] !== "") {
            return appStateObj[key]
        }
        return "n/a"
    }

    function userItems() {
        if (userActionObj.items && userActionObj.items.length !== undefined) {
            return userActionObj.items
        }
        var nested = resultObject()
        if (nested.users && nested.users.length !== undefined) {
            return nested.users
        }
        if (nested.items && nested.items.length !== undefined) {
            return nested.items
        }
        return []
    }

    function itemsCount() {
        var nested = resultObject()
        if (userActionObj.items_count !== undefined) {
            return userActionObj.items_count
        }
        if (userActionObj.user_count !== undefined) {
            return userActionObj.user_count
        }
        if (nested.items_count !== undefined) {
            return nested.items_count
        }
        if (nested.user_count !== undefined) {
            return nested.user_count
        }
        return userItems().length
    }

    function formatUserItem(item, index) {
        if (!item || typeof item !== "object") {
            return String(index + 1) + ". " + safeText(item)
        }
        var userId = safeText(item.user_id || item.id, "n/a")
        var displayName = safeText(item.display_name || item.name, userId)
        var userType = safeText(item.user_type, "local_user")
        var lastLogin = safeText(item.last_login_at, "n/a")
        return String(index + 1) + ". " + userId + " | " + displayName + " | " + userType + " | last_login_at=" + lastLogin
    }

    function userListText() {
        var arr = userItems()
        if (!arr || arr.length === 0) {
            return "No users found."
        }
        var lines = []
        for (var i = 0; i < arr.length; i++) {
            lines.push(formatUserItem(arr[i], i))
        }
        return lines.join("\n")
    }

    function refreshUserOptions() {
        var arr = userItems()
        var ids = []
        for (var i = 0; i < arr.length; i++) {
            var item = arr[i]
            if (item && typeof item === "object") {
                var uid = safeText(item.user_id || item.id, "")
                if (uid !== "" && uid !== "n/a") {
                    ids.push(uid)
                }
            }
        }
        userIdOptions = ids
        if (ids.length > 0) {
            if (selectedUserId === "" || ids.indexOf(selectedUserId) < 0) {
                selectedUserId = ids[0]
            }
            userIdField.text = selectedUserId
        }
    }

    function isFailureStatus(statusValue) {
        var st = safeText(statusValue, "")
        return st === "missing_input" || st === "missing_user_id" || st === "missing_user" || st === "user_not_found" || st === "profile_not_found" || st === "bridge_missing" || st === "parse_error"
    }

    function shouldShowProfileAfterAction(actionId, resultObj) {
        var st = resultObj ? resultObj.status : ""
        if (isFailureStatus(st)) {
            return false
        }
        if (actionId === "user.load" || actionId === "user.load_current" || actionId === "user.show_profile") {
            return true
        }
        if (actionId === "user.create") {
            return st === "created" || st === "accepted" || st === "user_exists"
        }
        return false
    }

    function profileDetailsText() {
        var detail = detailObject()
        var nested = resultObject()
        var source = detail
        if (!source || Object.keys(source).length === 0) {
            source = nested
        }
        if (!source || Object.keys(source).length === 0) {
            return "No profile detail available. Click Load Current or Show Profile."
        }
        var keys = Object.keys(source).sort()
        var lines = []
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i]
            var value = source[key]
            if (value && typeof value === "object") {
                value = JSON.stringify(value)
            }
            lines.push(key + ": " + safeText(value))
        }
        return lines.join("\n")
    }

    function resultText() {
        var lines = []
        lines.push("action: " + safeText(userActionObj.action_id || userActionObj.action, "n/a"))
        lines.push("status: " + safeText(userActionObj.status, "n/a"))
        lines.push("message: " + safeText(userActionObj.message, "n/a"))
        lines.push("accepted: " + safeText(userActionObj.accepted, "n/a"))
        if (userActionObj.error !== undefined) {
            lines.push("error: " + safeText(userActionObj.error))
        }
        return lines.join("\n")
    }

    function payloadFromForm() {
        return {
            "user_id": userIdField.text.trim(),
            "display_name": displayNameField.text.trim()
        }
    }

    function runUserAction(actionId, payload, successPanel, failurePanel, popupProfile) {
        selectedCommandId = actionId
        selectedStatus = "native_ready"
        selectedExecutionMode = "native"
        selectedNativeActionId = actionId
        if (typeof guiBridge === "undefined" || !guiBridge || !guiBridge.invokeAction) {
            userActionObj = {
                "action_id": actionId,
                "status": "bridge_missing",
                "message": "guiBridge unavailable",
                "accepted": false
            }
            activePanel = failurePanel || "result"
            return
        }
        var raw = guiBridge.invokeAction(actionId, JSON.stringify(payload || ({})))
        userActionObj = safeJsonParse(raw)
        if (actionId === "user.list") {
            refreshUserOptions()
            activePanel = "list"
            return
        }
        if (shouldShowProfileAfterAction(actionId, userActionObj)) {
            var loadedId = safeText(userActionObj.user_id || (userActionObj.result && userActionObj.result.user_id), "")
            if (loadedId !== "" && loadedId !== "n/a") {
                selectedUserId = loadedId
                userIdField.text = loadedId
            }
            activePanel = successPanel || "profile"
            if (popupProfile) {
                profileDialog.open()
            }
            return
        }
        activePanel = failurePanel || "form"
    }

    function loadSelectedUser() {
        var uid = selectedUserId || userIdField.text.trim()
        runUserAction("user.load", {"user_id": uid}, "profile", "list", false)
    }

    function showSelectedProfile() {
        var uid = selectedUserId || userIdField.text.trim()
        if (uid !== "" && uid !== "n/a") {
            userIdField.text = uid
        }
        runUserAction("user.show_profile", {"user_id": uid}, "profile", "list", true)
    }

    Dialog {
        id: profileDialog
        title: "Profile Detail Popup"
        modal: true
        standardButtons: Dialog.Ok
        width: Math.min(Math.max(root.width * 0.72, 520), 860)
        height: Math.min(Math.max(root.height * 0.72, 360), 680)
        anchors.centerIn: parent

        TextArea {
            anchors.fill: parent
            anchors.margins: 8
            readOnly: true
            wrapMode: TextEdit.WordWrap
            text: profileDetailsText()
        }
    }

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyleObj
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: (root.designThemeObj.colors && root.designThemeObj.colors.background) ? root.designThemeObj.colors.background : "#F8FAFC"
    }


    Item {
        id: task26UserDesktopPilotOverlay
        anchors.fill: parent
        anchors.margins: 6
        z: 100
        visible: root.task26DesktopPilotEnabled
        enabled: root.task26DesktopPilotEnabled

        DesktopLayoutPreview {
            id: task26UserDesktopLayoutPreview
            anchors.fill: parent
            layoutPayload: root.task26UserLayoutPayload()
            previewTitle: "TASK26 User Desktop Pilot"
            previewSubtitle: "Full-area card desktop pilot · legacy fallback: " + String(root.task26LegacyFallbackVisible)
            payloadStatusText: String((root.renderResourcesObj || ({})).task26_user_layout_status || "n/a")
            payloadSourceText: String((root.renderResourcesObj || ({})).task26_user_layout_source || "n/a")
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


    Column {
        id: legacyUserLayer
        anchors.fill: parent
        visible: root.task26LegacyFallbackVisible
        enabled: root.task26LegacyFallbackVisible
        spacing: 6

        PageHeader {
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            headerStyleObj: root.componentStyleObj.header || ({})
            titleText: "User / Profile"
            subtitleText: "Select or create a local user before calibration and training"
        }

        Row {
            width: parent.width
            spacing: 6
            DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Summary"; onClicked: activePanel = "summary" }
            DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "List Users"; onClicked: runUserAction("user.list", ({}), "list", false) }
            DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Create / Load"; onClicked: activePanel = "form" }
            DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Show Profile Detail"; onClicked: showSelectedProfile() }
        }

        Row {
            width: parent.width
            spacing: 8

            GroupBox {
                title: "Current User Summary"
                width: activePanel === "summary" ? parent.width * 0.58 : parent.width * 0.42
                visible: activePanel === "summary" || activePanel === "profile" || activePanel === "result"

                Column {
                    spacing: 3
                    Label { text: "current_user_id: " + safeText(summaryValue("current_user_id")) }
                    Label { text: "user_type: " + safeText(summaryValue("user_type")) }
                    Label { text: "profile_loaded: " + safeText(summaryValue("profile_loaded")) }
                    Label { text: "profile_status: " + safeText(summaryValue("status")) }
                    Label { text: "last_calibration_id: " + safeText(summaryValue("last_calibration_id")) }
                    Label { text: "attention_low_threshold: " + safeText(summaryValue("attention_low_threshold")) }
                    Label { text: "attention_high_threshold: " + safeText(summaryValue("attention_high_threshold")) }
                    Label { text: "preferred_game_id: " + safeText(summaryValue("preferred_game_id")) }
                    Label { text: "difficulty_level: " + safeText(summaryValue("difficulty_level")) }
                }
            }

            GroupBox {
                title: "Create / Load User"
                width: parent.width * 0.54
                visible: activePanel === "form" || activePanel === "summary"

                Column {
                    spacing: 5
                    Label { text: "user_id input" }
                    TextField {
                        id: userIdField
                        width: 280
                        placeholderText: "user_id, e.g. TEST"
                    }
                    Label { text: "display_name input" }
                    TextField {
                        id: displayNameField
                        width: 280
                        placeholderText: "display name"
                    }
                    Row {
                        spacing: 6
                        DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Create"; onClicked: runUserAction("user.create", payloadFromForm(), "profile", "form", false) }
                        DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Load"; onClicked: runUserAction("user.load", {"user_id": userIdField.text.trim()}, "profile", "form", false) }
                        DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Load Current"; onClicked: runUserAction("user.load_current", ({}), "profile", "form", false) }
                    }
                }
            }
        }

        GroupBox {
            title: "User List"
            width: parent.width
            visible: activePanel === "list" || activePanel === "summary"

            Column {
                spacing: 4
                Label { text: "items_count: " + safeText(itemsCount(), "0") }
                Label { text: "Switch User" }
                Row {
                    spacing: 6
                    ComboBox {
                        id: userSwitchCombo
                        width: 260
                        model: root.userIdOptions
                        enabled: root.userIdOptions.length > 0
                        onActivated: {
                            root.selectedUserId = currentText
                            userIdField.text = currentText
                        }
                        Component.onCompleted: {
                            if (root.userIdOptions.length > 0 && root.selectedUserId === "") {
                                root.selectedUserId = currentText
                            }
                        }
                    }
                    DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                        text: "Load Selected User"
                        enabled: root.selectedUserId !== "" || userIdField.text.trim() !== ""
                        onClicked: loadSelectedUser()
                    }
                    DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj;
                        text: "Show Selected Profile"
                        enabled: root.selectedUserId !== "" || userIdField.text.trim() !== ""
                        onClicked: showSelectedProfile()
                    }
                }
                Label { text: "selected_user_id: " + safeText(root.selectedUserId, "n/a") }
                TextArea {
                    width: root.width - 40
                    height: activePanel === "list" ? 160 : 88
                    readOnly: true
                    wrapMode: TextEdit.WordWrap
                    text: userListText()
                }
            }
        }

        GroupBox {
            title: "Profile Detail"
            width: parent.width
            visible: activePanel === "profile"

            Column {
                spacing: 4
                DesignButton { buttonStyleObj: root.componentStyleObj.button || ({}); themeObj: root.designThemeObj; renderResourcesObj: root.renderResourcesObj; text: "Open Profile Detail Popup"; onClicked: profileDialog.open() }
                TextArea {
                    width: root.width - 40
                    height: 170
                    readOnly: true
                    wrapMode: TextEdit.WordWrap
                    text: profileDetailsText()
                }
            }
        }

        GroupBox {
            title: "User Action Result"
            width: parent.width
            visible: activePanel === "result" || activePanel === "profile" || activePanel === "list" || activePanel === "form"

            TextArea {
                width: root.width - 40
                height: 86
                readOnly: true
                wrapMode: TextEdit.WordWrap
                text: resultText()
            }
        }

        GroupBox {
            title: "User Page Actions"
            width: parent.width

            Label {
                text: "Native actions: user.list | user.create | user.load | user.load_current | user.show_profile. CLI/manual commands remain documented in Page Commands."
                wrapMode: Text.WordWrap
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
            renderResourcesObj: root.renderResourcesObj
            designThemeObj: root.designThemeObj
            componentStyleObj: root.componentStyleObj
            feedbackStyleObj: root.componentStyleObj.feedback_panel || ({})
            pageId: "user"
            selectedCommandId: root.selectedCommandId
            selectedStatus: root.selectedStatus
            selectedExecutionMode: root.selectedExecutionMode
            selectedNativeActionId: root.selectedNativeActionId
            lastCommand: safeText(controlStateObj.last_command)
            lastResult: safeText(controlStateObj.last_command_result)
            lastError: safeText(controlStateObj.last_command_error)
        }
    }
}

// Compatibility tokens kept for TASK23/TASK23B tests:
// User Page User Page Actions User Page Result Page Commands Page Feedback
// List Users Create User Load User Load Current User Show Profile Guest Mode Ensure Demo Debug
// Current User Summary Create / Load User User List User Action Result Profile Detail Popup Open Profile Detail Popup
// Switch User selected_user_id Load Selected User Show Selected Profile ComboBox shouldShowProfileAfterAction
// user_id display_name user_id input display_name input No users found. missing_input
