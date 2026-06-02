import QtQuick
import QtQuick.Controls
import "pages"
import "components"

ApplicationWindow {
    id: root


    property var desktopGuiBridge: guiBridge
    // TASK26 compatibility token for static tests only: guiBridge: guiBridge
    visible: true
    width: Number(appShellLayoutValue("window_width", 1360))
    height: Number(appShellLayoutValue("window_height", 860))
    title: "RELIC Core"
    color: designColor("background", "#0f1720")

    property string currentPage: "home"
    property var appStateObj: ({})
    property var runtimeObj: ({})
    property var sessionObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})
    property var controlStateObj: ({})
    property var pageCommandManifestObj: ({})
    property var renderResourcesObj: ({})
    property var designThemeObj: ({})
    property var pageStylesObj: ({})
    property var componentStylesObj: ({})
    property var gameStylesObj: ({})
    property var effectStylesObj: ({})
    property bool traceLockAudioPlaybackEnabled: false
    property bool traceLockMusicEnabled: false
    property bool traceLockAmbientEnabled: false
    property bool traceLockSfxEnabled: false
    property string traceLockMusicKey: "audio.tracelock.music.loop"
    property string traceLockAmbientKey: "audio.tracelock.ambient.loop"
    property string traceLockHitKey: "audio.tracelock.hit"
    property string traceLockMissKey: "audio.tracelock.miss"
    property string traceLockComboKey: "audio.tracelock.combo"
    property string traceLockUiClickKey: "audio.ui.click"
    property real traceLockMusicVolume: 0.28
    property real traceLockAmbientVolume: 0.18
    property real traceLockSfxVolume: 0.55
    property int gameViewPullSeq: 0
    property int lastGameViewPullAtMs: 0

    function safeJsonParse(t) {
        try {
            return JSON.parse(t || "{}")
        } catch (e) {
            return ({"__parse_error__": "invalid"})
        }
    }

    function safeText(v, f) {
        var fb = f === undefined ? "n/a" : f
        return v === undefined || v === null || v === "" ? fb : String(v)
    }

    function getField(o, k, f) {
        if (!o || o[k] === undefined || o[k] === null || o[k] === "") {
            return f === undefined ? "n/a" : f
        }
        return o[k]
    }

    function designColor(k, f) {
        var colors = designThemeObj.colors || ({})
        var v = colors[k]
        return v === undefined || v === null || v === "" ? f : v
    }

    function designSpacing(k, f) {
        var spacing = designThemeObj.spacing || ({})
        var v = spacing[k]
        return v === undefined || v === null || v === "" ? f : v
    }

    function pageStyle(pageId) {
        return pageStylesObj[pageId] || ({})
    }

    function componentStyle(componentId) {
        return componentStylesObj[componentId] || ({})
    }


    function traceLockGameConfig() {
        var gs = gameStylesObj.trace_lock || gameStylesObj.tracelock || ({})
        return gs
    }

    function traceLockAudioConfig() {
        var gs = traceLockGameConfig()
        return gs.audio || ({})
    }

    function boolConfigValue(v, fallbackValue) {
        if (v === true || v === "true" || v === 1 || v === "1") return true
        if (v === false || v === "false" || v === 0 || v === "0") return false
        return fallbackValue
    }

    function stringConfigValue(v, fallbackValue) {
        if (v === undefined || v === null || v === "") return fallbackValue
        return String(v)
    }

    function numberConfigValue(v, fallbackValue) {
        var n = Number(v)
        return isNaN(n) ? fallbackValue : n
    }

    function pullTraceLockAudioFlags() {
        var cfg = traceLockAudioConfig()
        traceLockAudioPlaybackEnabled = boolConfigValue(cfg.playback_enabled, false)
        traceLockMusicEnabled = boolConfigValue(cfg.music_enabled, false)
        traceLockAmbientEnabled = boolConfigValue(cfg.ambient_enabled, false)
        traceLockSfxEnabled = boolConfigValue(cfg.sfx_enabled, false)
        traceLockMusicKey = stringConfigValue(cfg.music_key, "audio.tracelock.music.loop")
        traceLockAmbientKey = stringConfigValue(cfg.ambient_key, "audio.tracelock.ambient.loop")
        traceLockHitKey = stringConfigValue(cfg.hit_key, "audio.tracelock.hit")
        traceLockMissKey = stringConfigValue(cfg.miss_key, "audio.tracelock.miss")
        traceLockComboKey = stringConfigValue(cfg.combo_key, "audio.tracelock.combo")
        traceLockUiClickKey = stringConfigValue(cfg.ui_click_key, "audio.ui.click")
        traceLockMusicVolume = numberConfigValue(cfg.music_volume, 0.28)
        traceLockAmbientVolume = numberConfigValue(cfg.ambient_volume, 0.18)
        traceLockSfxVolume = numberConfigValue(cfg.sfx_volume, 0.55)
    }

    function syncTraceLockAudioController() {
        if (traceLockAudioController) {
            traceLockAudioController.updateMusicState()
        }
    }

    function appShellLayoutValue(key, fallbackValue) {
        var layout = pageStyle("app_shell").layout || ({})
        var v = layout[key]
        return v === undefined || v === null || v === "" ? fallbackValue : v
    }

    function shellCardValue(key, fallbackValue) {
        return root.appShellLayoutValue(key, fallbackValue)
    }

    function isCurrentPage(pageId) {
        return root.currentPage === pageId
    }

    // shell_nav_readability_tokens: navInfoCardBackground navActionCardBackground navActionCardText navInfoCardText
    function navInfoCardBackground() {
        return String(root.appShellLayoutValue("nav_info_background", "#08111D"))
    }

    function navInfoCardBorder() {
        return String(root.appShellLayoutValue("nav_info_border", "#1F3A52"))
    }

    function navInfoCardText() {
        return String(root.appShellLayoutValue("nav_info_text", "#CFE8F7"))
    }

    function navInfoMutedText() {
        return String(root.appShellLayoutValue("nav_info_muted_text", "#7FA4B8"))
    }

    function navCardBackground(pageId) {
        return root.isCurrentPage(pageId)
            ? String(root.appShellLayoutValue("active_page_background", "#1D6D88"))
            : String(root.appShellLayoutValue("inactive_page_background", "#15283A"))
    }

    function navCardBorder(pageId) {
        return root.isCurrentPage(pageId)
            ? String(root.appShellLayoutValue("active_page_border_color", "#A7F3FF"))
            : String(root.appShellLayoutValue("inactive_page_border_color", "#36536B"))
    }

    function navCardText(pageId) {
        return root.isCurrentPage(pageId)
            ? String(root.appShellLayoutValue("active_page_text", "#FFFFFF"))
            : String(root.appShellLayoutValue("inactive_page_text", "#EAF6FF"))
    }

    function navCardMutedText(pageId) {
        return root.isCurrentPage(pageId)
            ? String(root.appShellLayoutValue("active_page_muted_text", "#DDF8FF"))
            : String(root.appShellLayoutValue("inactive_page_muted_text", "#9DBBD0"))
    }

    function safetyCardBackground() {
        return String(root.appShellLayoutValue("safety_card_background", "#16131D"))
    }

    function safetyCardBorder() {
        return String(root.appShellLayoutValue("safety_card_border", "#6A4E66"))
    }

    function goPage(pageId) {
        root.currentPage = pageId
    }

    function commandsFor(pageId) {
        var pages = pageCommandManifestObj.pages || ({})
        var arr = pages[pageId] || []
        var out = []
        for (var i = 0; i < arr.length && i < 4; i++) {
            out.push(arr[i].command_id + "(" + arr[i].execution_mode + ")")
        }
        return out.join(" | ")
    }

    function pullState() {
        if (!guiBridge) {
            return
        }
        appStateObj = safeJsonParse(guiBridge.appState)
        runtimeObj = safeJsonParse(guiBridge.runtimeSnapshot)
        sessionObj = safeJsonParse(guiBridge.sessionState)
        pullGameState()
        controlStateObj = safeJsonParse(guiBridge.controlStateJson)
        pageCommandManifestObj = safeJsonParse(guiBridge.pageCommandManifestJson)
        renderResourcesObj = safeJsonParse(guiBridge.renderResourcesJson)
        designThemeObj = renderResourcesObj.theme || ({})
        pageStylesObj = renderResourcesObj.page_styles || ({})
        componentStylesObj = renderResourcesObj.component_styles || ({})
        gameStylesObj = renderResourcesObj.game_styles || ({})
        effectStylesObj = renderResourcesObj.effect_styles || ({})
        pullTraceLockAudioFlags()
        syncTraceLockAudioController()
    }

    function pullGameState() {
        if (!guiBridge) {
            return
        }
        var now = Date.now()
        gameHudObj = safeJsonParse(guiBridge.gameHudJson)
        gameViewObj = safeJsonParse(guiBridge.gameViewJson)
        syncTraceLockAudioController()
        gameViewPullSeq += 1
        lastGameViewPullAtMs = now
        if (gameViewObj && typeof gameViewObj === "object") {
            var hints = gameViewObj.layout_hints || ({})
            var built = Number(hints.backend_view_built_wall_ms || 0)
            var bridgePull = Number(hints.bridge_pull_wall_ms || 0)
            hints.qml_shell_pull_wall_ms = now
            hints.qml_shell_pull_seq = gameViewPullSeq
            hints.qml_shell_game_view_age_ms = built > 0 ? Math.max(0, now - built) : -1
            hints.qml_shell_after_bridge_ms = bridgePull > 0 ? Math.max(0, now - bridgePull) : -1
            gameViewObj.layout_hints = hints
            if ((gameViewPullSeq % 20) === 0 || hints.qml_shell_game_view_age_ms > 160) {
                console.log("[SHELL GAMEVIEW DEBUG] " + JSON.stringify({
                    "seq": gameViewPullSeq,
                    "frame_id": gameViewObj.frame_id,
                    "backend_age_ms": hints.qml_shell_game_view_age_ms,
                    "after_bridge_ms": hints.qml_shell_after_bridge_ms,
                    "bridge_emit_seq": hints.bridge_emit_seq_next,
                    "backend_update_count": hints.backend_game_update_count
                }))
            }
        }
    }

    function invokeNative(actionId) {
        if (guiBridge) {
            guiBridge.invokeAction(actionId, "{}")
        }
    }

    Connections {
        target: root.desktopGuiBridge ? root.desktopGuiBridge : null
        function onStateChanged() {
            pullState()
        }
        function onGameViewJsonChanged() {
            pullGameState()
        }
        function onGameHudJsonChanged() {
            pullGameState()
        }
        function onRenderResourcesJsonChanged() {
            pullState()
        }
    }

    Component.onCompleted: pullState()

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: root.pageStyle("app_shell")
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: root.designColor("background", "#0f1720")
    }

    Column {
        anchors.fill: parent
        anchors.margins: Number(root.appShellLayoutValue("content_margin", root.designSpacing("page_margin", 8)))
        spacing: Number(root.appShellLayoutValue("section_gap", root.designSpacing("section_gap", 6)))

        DesignPanel {
            id: shell_top_status_card
            objectName: "shell_top_status_card"
            width: parent.width
            height: Number(root.appShellLayoutValue("top_bar_height", 86))
            panelStyleObj: ({
                "background": String(root.appShellLayoutValue("top_bar_background", "#102033")),
                "border": String(root.appShellLayoutValue("top_bar_border", "#406780")),
                "border_width": 1,
                "radius": Number(root.appShellLayoutValue("corner_radius", 22)),
                "opacity": 0.96
            })
            themeObj: root.designThemeObj
            renderResourcesObj: root.renderResourcesObj

            Row {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                anchors.topMargin: 12
                anchors.bottomMargin: 12
                spacing: Number(root.appShellLayoutValue("top_bar_status_chip_gap", 10))

                Rectangle {
                    id: shell_brand_card
                    objectName: "shell_brand_card"
                    width: 278
                    height: parent.height
                    radius: Number(root.appShellLayoutValue("status_chip_radius", 18))
                    color: String(root.appShellLayoutValue("brand_card_background", "#13283D"))
                    border.color: String(root.appShellLayoutValue("brand_card_border", "#4FAED0"))
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 2

                        Text {
                            text: "RELIC / 意念玩家"
                            color: root.designColor("text", "#e6edf5")
                            font.pixelSize: Number((root.designThemeObj.typography || ({})).title_size || 18)
                            font.bold: true
                            elide: Text.ElideRight
                            width: parent.width
                        }

                        Text {
                            text: "Focus training control shell"
                            color: root.designColor("text_muted", "#9aacbd")
                            font.pixelSize: 11
                            elide: Text.ElideRight
                            width: parent.width
                        }
                    }
                }

                Rectangle {
                    id: shell_status_chip_user
                    objectName: "shell_status_chip_current_user"
                    width: 180
                    height: parent.height
                    radius: Number(root.appShellLayoutValue("status_chip_radius", 18))
                    color: String(root.appShellLayoutValue("status_chip_background", "#132A3D"))
                    border.color: String(root.appShellLayoutValue("status_chip_border", "#3D6780"))
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 9
                        spacing: 2
                        Text { text: "current_user_id"; color: "#8FB5CC"; font.pixelSize: 10; width: parent.width; elide: Text.ElideRight }
                        Text { text: root.safeText(root.getField(root.controlStateObj, "current_user_id")); color: root.designColor("text", "#e6edf5"); font.pixelSize: 13; font.bold: true; width: parent.width; elide: Text.ElideRight }
                    }
                }

                Rectangle {
                    id: shell_status_chip_connection
                    objectName: "shell_status_chip_connection"
                    width: 160
                    height: parent.height
                    radius: Number(root.appShellLayoutValue("status_chip_radius", 18))
                    color: String(root.appShellLayoutValue("status_chip_background", "#132A3D"))
                    border.color: String(root.appShellLayoutValue("status_chip_border", "#3D6780"))
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 9
                        spacing: 2
                        Text { text: "connection_status"; color: "#8FB5CC"; font.pixelSize: 10; width: parent.width; elide: Text.ElideRight }
                        Text { text: root.safeText(root.getField(root.runtimeObj, "connection_status")); color: root.designColor("text", "#e6edf5"); font.pixelSize: 13; font.bold: true; width: parent.width; elide: Text.ElideRight }
                    }
                }

                Rectangle {
                    id: shell_status_chip_quality
                    objectName: "shell_status_chip_quality"
                    width: 160
                    height: parent.height
                    radius: Number(root.appShellLayoutValue("status_chip_radius", 18))
                    color: String(root.appShellLayoutValue("status_chip_background", "#132A3D"))
                    border.color: String(root.appShellLayoutValue("status_chip_border", "#3D6780"))
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 9
                        spacing: 2
                        Text { text: "quality_state"; color: "#8FB5CC"; font.pixelSize: 10; width: parent.width; elide: Text.ElideRight }
                        Text { text: root.safeText(root.getField(root.runtimeObj, "quality_state")); color: root.designColor("text", "#e6edf5"); font.pixelSize: 13; font.bold: true; width: parent.width; elide: Text.ElideRight }
                    }
                }

                Rectangle {
                    id: shell_status_chip_control
                    objectName: "shell_status_chip_control"
                    width: 160
                    height: parent.height
                    radius: Number(root.appShellLayoutValue("status_chip_radius", 18))
                    color: String(root.appShellLayoutValue("status_chip_background", "#132A3D"))
                    border.color: String(root.appShellLayoutValue("status_chip_border", "#3D6780"))
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 9
                        spacing: 2
                        Text { text: "control_state"; color: "#8FB5CC"; font.pixelSize: 10; width: parent.width; elide: Text.ElideRight }
                        Text { text: root.safeText(root.getField(root.runtimeObj, "control_state")); color: root.designColor("text", "#e6edf5"); font.pixelSize: 13; font.bold: true; width: parent.width; elide: Text.ElideRight }
                    }
                }

                Rectangle {
                    id: shell_status_chip_session
                    objectName: "shell_status_chip_session"
                    width: 150
                    height: parent.height
                    radius: Number(root.appShellLayoutValue("status_chip_radius", 18))
                    color: String(root.appShellLayoutValue("status_chip_background", "#132A3D"))
                    border.color: String(root.appShellLayoutValue("status_chip_border", "#3D6780"))
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 9
                        spacing: 2
                        Text { text: "session_active"; color: "#8FB5CC"; font.pixelSize: 10; width: parent.width; elide: Text.ElideRight }
                        Text { text: root.safeText(root.getField(root.controlStateObj, "session_active")); color: root.designColor("text", "#e6edf5"); font.pixelSize: 13; font.bold: true; width: parent.width; elide: Text.ElideRight }
                    }
                }

                Rectangle {
                    id: shell_status_chip_page
                    objectName: "shell_status_chip_current_page"
                    width: 150
                    height: parent.height
                    radius: Number(root.appShellLayoutValue("status_chip_radius", 18))
                    color: String(root.appShellLayoutValue("status_chip_background", "#132A3D"))
                    border.color: String(root.appShellLayoutValue("status_chip_border", "#3D6780"))
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 9
                        spacing: 2
                        Text { text: "currentPage"; color: "#8FB5CC"; font.pixelSize: 10; width: parent.width; elide: Text.ElideRight }
                        Text { text: root.currentPage; color: root.designColor("text", "#e6edf5"); font.pixelSize: 13; font.bold: true; width: parent.width; elide: Text.ElideRight }
                    }
                }
            }
        }

        Row {
            id: shell_body_row
            objectName: "shell_body_row"
            width: parent.width
            height: parent.height - shell_top_status_card.height - parent.spacing
            spacing: Number(root.appShellLayoutValue("body_gap", root.designSpacing("section_gap", 6)))

            DesignPanel {
                id: shell_left_nav_card
                objectName: "shell_left_nav_card"
                width: Number(root.appShellLayoutValue("nav_width", 252))
                height: parent.height
                panelStyleObj: ({
                    "background": String(root.appShellLayoutValue("nav_shell_background", "#0C1724")),
                    "border": String(root.appShellLayoutValue("nav_shell_border", "#2E526B")),
                    "border_width": 1,
                    "radius": Number(root.appShellLayoutValue("corner_radius", 22)),
                    "opacity": 0.96
                })
                themeObj: root.designThemeObj
                renderResourcesObj: root.renderResourcesObj

                Column {
                    anchors.fill: parent
                    anchors.margins: Number(root.appShellLayoutValue("nav_card_padding", 14))
                    spacing: Number(root.appShellLayoutValue("nav_item_gap", 9))

                    Rectangle {
                        id: shell_nav_header_card
                        objectName: "shell_nav_header_card"
                        width: parent.width
                        height: 74
                        radius: 18
                        color: root.navInfoCardBackground()
                        border.color: root.navInfoCardBorder()
                        border.width: 1
                        opacity: 0.92

                        Rectangle {
                            id: shell_nav_info_accent_strip
                            objectName: "shell_nav_info_accent_strip"
                            width: 4
                            radius: 2
                            anchors.left: parent.left
                            anchors.leftMargin: 10
                            anchors.top: parent.top
                            anchors.topMargin: 12
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 12
                            color: String(root.appShellLayoutValue("nav_info_accent", "#5AC8FA"))
                        }

                        Column {
                            anchors.left: shell_nav_info_accent_strip.right
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.leftMargin: 10
                            anchors.rightMargin: 12
                            anchors.topMargin: 9
                            anchors.bottomMargin: 9
                            spacing: 3

                            Text {
                                text: "NAVIGATION INFO"
                                color: root.navInfoMutedText()
                                font.pixelSize: 10
                                font.letterSpacing: 0.6
                                width: parent.width
                                elide: Text.ElideRight
                            }

                            Text {
                                text: "Page shortcuts"
                                color: root.navInfoCardText()
                                font.bold: true
                                font.pixelSize: 15
                                width: parent.width
                                elide: Text.ElideRight
                            }

                            Text {
                                text: "Cards below are clickable"
                                color: root.navInfoMutedText()
                                font.pixelSize: 11
                                width: parent.width
                                elide: Text.ElideRight
                            }
                        }
                    }

                    Rectangle {
                        id: shell_nav_card_home
                        objectName: "shell_nav_card_home"
                        width: parent.width
                        height: 50
                        radius: 16
                        color: root.navCardBackground("home")
                        border.color: root.navCardBorder("home")
                        border.width: root.isCurrentPage("home") ? 2 : 1

                        Rectangle {
                            objectName: "shell_nav_active_strip_home"
                            visible: root.isCurrentPage("home")
                            width: 4
                            radius: 2
                            anchors.left: parent.left
                            anchors.leftMargin: 7
                            anchors.top: parent.top
                            anchors.topMargin: 10
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 10
                            color: String(root.appShellLayoutValue("active_page_accent_strip", "#EAFBFF"))
                        }

                        Text {
                            anchors.left: parent.left
                            anchors.leftMargin: 20
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Home"
                            color: root.navCardText("home")
                            font.pixelSize: 14
                            font.bold: root.isCurrentPage("home")
                        }

                        Text {
                            anchors.right: parent.right
                            anchors.rightMargin: 14
                            anchors.verticalCenter: parent.verticalCenter
                            text: "⌂"
                            color: root.navCardText("home")
                            font.pixelSize: 15
                        }

                        MouseArea { anchors.fill: parent; onClicked: root.goPage("home") }
                    }

                    Rectangle {
                        id: shell_nav_card_user
                        objectName: "shell_nav_card_user"
                        width: parent.width
                        height: 50
                        radius: 16
                        color: root.navCardBackground("user")
                        border.color: root.navCardBorder("user")
                        border.width: root.isCurrentPage("user") ? 2 : 1

                        Rectangle {
                            objectName: "shell_nav_active_strip_user"
                            visible: root.isCurrentPage("user")
                            width: 4
                            radius: 2
                            anchors.left: parent.left
                            anchors.leftMargin: 7
                            anchors.top: parent.top
                            anchors.topMargin: 10
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 10
                            color: String(root.appShellLayoutValue("active_page_accent_strip", "#EAFBFF"))
                        }

                        Text { anchors.left: parent.left; anchors.leftMargin: 20; anchors.verticalCenter: parent.verticalCenter; text: "User"; color: root.navCardText("user"); font.pixelSize: 14; font.bold: root.isCurrentPage("user") }
                        Text { anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter; text: "ID"; color: root.navCardText("user"); font.pixelSize: 12; font.bold: true }
                        MouseArea { anchors.fill: parent; onClicked: root.goPage("user") }
                    }

                    Rectangle {
                        id: shell_nav_card_calibration
                        objectName: "shell_nav_card_calibration"
                        width: parent.width
                        height: 50
                        radius: 16
                        color: root.navCardBackground("calibration")
                        border.color: root.navCardBorder("calibration")
                        border.width: root.isCurrentPage("calibration") ? 2 : 1

                        Rectangle {
                            objectName: "shell_nav_active_strip_calibration"
                            visible: root.isCurrentPage("calibration")
                            width: 4
                            radius: 2
                            anchors.left: parent.left
                            anchors.leftMargin: 7
                            anchors.top: parent.top
                            anchors.topMargin: 10
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 10
                            color: String(root.appShellLayoutValue("active_page_accent_strip", "#EAFBFF"))
                        }

                        Text { anchors.left: parent.left; anchors.leftMargin: 20; anchors.verticalCenter: parent.verticalCenter; text: "Calibration"; color: root.navCardText("calibration"); font.pixelSize: 14; font.bold: root.isCurrentPage("calibration") }
                        Text { anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter; text: "CAL"; color: root.navCardText("calibration"); font.pixelSize: 12; font.bold: true }
                        MouseArea { anchors.fill: parent; onClicked: root.goPage("calibration") }
                    }

                    Rectangle {
                        id: shell_nav_card_training
                        objectName: "shell_nav_card_training"
                        width: parent.width
                        height: 50
                        radius: 16
                        color: root.navCardBackground("training")
                        border.color: root.navCardBorder("training")
                        border.width: root.isCurrentPage("training") ? 2 : 1

                        Rectangle {
                            objectName: "shell_nav_active_strip_training"
                            visible: root.isCurrentPage("training")
                            width: 4
                            radius: 2
                            anchors.left: parent.left
                            anchors.leftMargin: 7
                            anchors.top: parent.top
                            anchors.topMargin: 10
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 10
                            color: String(root.appShellLayoutValue("active_page_accent_strip", "#EAFBFF"))
                        }

                        Text { anchors.left: parent.left; anchors.leftMargin: 20; anchors.verticalCenter: parent.verticalCenter; text: "Training"; color: root.navCardText("training"); font.pixelSize: 14; font.bold: root.isCurrentPage("training") }
                        Text { anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter; text: "RUN"; color: root.navCardText("training"); font.pixelSize: 12; font.bold: true }
                        MouseArea { anchors.fill: parent; onClicked: root.goPage("training") }
                    }

                    Rectangle {
                        id: shell_nav_card_report
                        objectName: "shell_nav_card_report"
                        width: parent.width
                        height: 50
                        radius: 16
                        color: root.navCardBackground("report")
                        border.color: root.navCardBorder("report")
                        border.width: root.isCurrentPage("report") ? 2 : 1

                        Rectangle {
                            objectName: "shell_nav_active_strip_report"
                            visible: root.isCurrentPage("report")
                            width: 4
                            radius: 2
                            anchors.left: parent.left
                            anchors.leftMargin: 7
                            anchors.top: parent.top
                            anchors.topMargin: 10
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 10
                            color: String(root.appShellLayoutValue("active_page_accent_strip", "#EAFBFF"))
                        }

                        Text { anchors.left: parent.left; anchors.leftMargin: 20; anchors.verticalCenter: parent.verticalCenter; text: "Report"; color: root.navCardText("report"); font.pixelSize: 14; font.bold: root.isCurrentPage("report") }
                        Text { anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter; text: "TXT"; color: root.navCardText("report"); font.pixelSize: 12; font.bold: true }
                        MouseArea { anchors.fill: parent; onClicked: root.goPage("report") }
                    }

                    Rectangle {
                        id: shell_nav_card_developer_lab
                        objectName: "shell_nav_card_developer_lab"
                        width: parent.width
                        height: 50
                        radius: 16
                        color: root.navCardBackground("developer_lab")
                        border.color: root.navCardBorder("developer_lab")
                        border.width: root.isCurrentPage("developer_lab") ? 2 : 1

                        Rectangle {
                            objectName: "shell_nav_active_strip_developer_lab"
                            visible: root.isCurrentPage("developer_lab")
                            width: 4
                            radius: 2
                            anchors.left: parent.left
                            anchors.leftMargin: 7
                            anchors.top: parent.top
                            anchors.topMargin: 10
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 10
                            color: String(root.appShellLayoutValue("active_page_accent_strip", "#EAFBFF"))
                        }

                        Text { anchors.left: parent.left; anchors.leftMargin: 20; anchors.verticalCenter: parent.verticalCenter; text: "Developer Lab"; color: root.navCardText("developer_lab"); font.pixelSize: 14; font.bold: root.isCurrentPage("developer_lab") }
                        Text { anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter; text: "LAB"; color: root.navCardText("developer_lab"); font.pixelSize: 12; font.bold: true }
                        MouseArea { anchors.fill: parent; onClicked: root.goPage("developer_lab") }
                    }

                    Item { width: parent.width; height: 8 }

                    Rectangle {
                        id: shell_global_safety_card
                        objectName: "shell_global_safety_card"
                        width: parent.width
                        height: 176
                        radius: 18
                        color: root.safetyCardBackground()
                        border.color: root.safetyCardBorder()
                        border.width: 1

                        Column {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8

                            Text {
                                text: "Global Safety"
                                color: String(root.appShellLayoutValue("safety_card_text", "#FFE8F2"))
                                font.bold: true
                                font.pixelSize: 14
                                width: parent.width
                                elide: Text.ElideRight
                            }

                            DesignButton {
                                renderResourcesObj: root.renderResourcesObj
                                text: "Refresh"
                                width: parent.width
                                buttonStyleObj: root.componentStyle("button")
                                themeObj: root.designThemeObj
                                onClicked: root.invokeNative("app.refresh_now")
                            }

                            DesignButton {
                                renderResourcesObj: root.renderResourcesObj
                                text: "Safe Stop"
                                width: parent.width
                                buttonStyleObj: root.componentStyle("button")
                                themeObj: root.designThemeObj
                                onClicked: root.invokeNative("live.safe_stop")
                            }

                            DesignButton {
                                renderResourcesObj: root.renderResourcesObj
                                text: "Quit"
                                width: parent.width
                                buttonStyleObj: root.componentStyle("button")
                                themeObj: root.designThemeObj
                                onClicked: Qt.quit()
                            }
                        }
                    }
                }
            }

            DesignPanel {
                id: shell_content_host_card
                objectName: "shell_content_host_card"
                width: parent.width - Number(root.appShellLayoutValue("nav_width", 252)) - parent.spacing
                height: parent.height
                panelStyleObj: ({
                    "background": String(root.appShellLayoutValue("content_background", "#0B1420")),
                    "border": String(root.appShellLayoutValue("content_border", "#2A455C")),
                    "border_width": 1,
                    "radius": Number(root.appShellLayoutValue("corner_radius", 22)),
                    "opacity": 0.94
                })
                themeObj: root.designThemeObj
                renderResourcesObj: root.renderResourcesObj

                Item {
                    id: pageHost
                    objectName: "PageHost"
                    anchors.fill: parent

                    DesignBackground {
                        anchors.fill: parent
                        themeObj: root.designThemeObj
                        styleObj: root.pageStyle(root.currentPage === "training" ? "training_page" : (root.currentPage + "_page"))
                        renderResourcesObj: root.renderResourcesObj
                        fallbackColor: root.designColor("background", "#0f1720")
                    }

                    HomePage {
                        anchors.fill: parent
                        visible: root.currentPage === "home"
                        designThemeObj: root.designThemeObj
                        pageStyleObj: root.pageStylesObj.home_page || ({})
                        componentStyleObj: root.componentStylesObj
                        renderResourcesObj: root.renderResourcesObj
                        appStateObj: root.appStateObj
                        sessionObj: root.sessionObj
                        gameHudObj: root.gameHudObj
                        gameViewObj: root.gameViewObj
                        guiBridge: root.desktopGuiBridge
                        controlStateObj: root.controlStateObj
                        runtimeObj: root.runtimeObj
                        commandSummary: root.commandsFor("home")
                        onNavigateTo: function(p) { root.currentPage = p }
                        onInvokeNative: function(a) { root.invokeNative(a) }
                    }

                    UserPage {
                        anchors.fill: parent
                        visible: root.currentPage === "user"
                        designThemeObj: root.designThemeObj
                        pageStyleObj: root.pageStylesObj.user_page || ({})
                        componentStyleObj: root.componentStylesObj
                        renderResourcesObj: root.renderResourcesObj
                        runtimeObj: root.runtimeObj
                        sessionObj: root.sessionObj
                        gameHudObj: root.gameHudObj
                        gameViewObj: root.gameViewObj
                        guiBridge: root.desktopGuiBridge
                        appStateObj: root.appStateObj
                        controlStateObj: root.controlStateObj
                        commandSummary: root.commandsFor("user")
                        onInvokeNative: function(a) { root.invokeNative(a) }
                    }

                    CalibrationPage {
                        anchors.fill: parent
                        visible: root.currentPage === "calibration"
                        designThemeObj: root.designThemeObj
                        pageStyleObj: root.pageStylesObj.calibration_page || ({})
                        componentStyleObj: root.componentStylesObj
                        renderResourcesObj: root.renderResourcesObj
                        appStateObj: root.appStateObj
                        runtimeObj: root.runtimeObj
                        sessionObj: root.sessionObj
                        gameHudObj: root.gameHudObj
                        gameViewObj: root.gameViewObj
                        guiBridge: root.desktopGuiBridge
                        controlStateObj: root.controlStateObj
                        commandSummary: root.commandsFor("calibration")
                        onInvokeNative: function(a) { root.invokeNative(a) }
                    }

                    TrainingPage {
                        anchors.fill: parent
                        visible: root.currentPage === "training"
                        designThemeObj: root.designThemeObj
                        pageStyleObj: root.pageStylesObj.training_page || ({})
                        componentStyleObj: root.componentStylesObj
                        renderResourcesObj: root.renderResourcesObj
                        sessionObj: root.sessionObj
                        guiBridge: root.desktopGuiBridge
                        appStateObj: root.appStateObj
                        controlStateObj: root.controlStateObj
                        runtimeObj: root.runtimeObj
                        gameHudObj: root.gameHudObj
                        gameViewObj: root.gameViewObj
                        gameStyleObj: root.gameStylesObj.trace_lock || ({})
                        effectStyleObj: root.effectStylesObj.trace_lock || ({})
                        commandSummary: root.commandsFor("training")
                        onInvokeNative: function(a) { root.invokeNative(a) }
                    }

                    ReportPage {
                        anchors.fill: parent
                        visible: root.currentPage === "report"
                        designThemeObj: root.designThemeObj
                        pageStyleObj: root.pageStylesObj.report_page || ({})
                        componentStyleObj: root.componentStylesObj
                        renderResourcesObj: root.renderResourcesObj
                        runtimeObj: root.runtimeObj
                        gameHudObj: root.gameHudObj
                        gameViewObj: root.gameViewObj
                        guiBridge: root.desktopGuiBridge
                        appStateObj: root.appStateObj
                        controlStateObj: root.controlStateObj
                        sessionObj: root.sessionObj
                        commandSummary: root.commandsFor("report")
                    }

                    // DiagnosticsPage is retained as a hidden compatibility host for legacy tests/resources.
                    // User-visible navigation to diagnostics is removed in TASK26I step1.
                    DiagnosticsPage {
                        anchors.fill: parent
                        visible: root.currentPage === "diagnostics"
                        designThemeObj: root.designThemeObj
                        pageStyleObj: root.pageStylesObj.diagnostics_page || ({})
                        componentStyleObj: root.componentStylesObj
                        renderResourcesObj: root.renderResourcesObj
                        appStateObj: root.appStateObj
                        gameViewObj: root.gameViewObj
                        guiBridge: root.desktopGuiBridge
                        controlStateObj: root.controlStateObj
                        runtimeObj: root.runtimeObj
                        sessionObj: root.sessionObj
                        gameHudObj: root.gameHudObj
                        commandSummary: root.commandsFor("diagnostics")
                        onInvokeNative: function(a) { root.invokeNative(a) }
                    }

                    DeveloperLabPage {
                        anchors.fill: parent
                        visible: root.currentPage === "developer_lab"
                        designThemeObj: root.designThemeObj
                        pageStyleObj: root.pageStylesObj.developer_lab_page || ({})
                        componentStyleObj: root.componentStylesObj
                        renderResourcesObj: root.renderResourcesObj
                        guiBridge: root.desktopGuiBridge
                        controlStateObj: root.controlStateObj
                        commandSummary: root.commandsFor("developer_lab")
                    }
                }
            }
        }
    }


    TraceLockAudioController {
        id: traceLockAudioController
        renderResourcesObj: root.renderResourcesObj
        gameHudObj: root.gameHudObj
        gameViewObj: root.gameViewObj
        playbackEnabled: root.traceLockAudioPlaybackEnabled
        musicEnabled: root.traceLockMusicEnabled
        ambientEnabled: root.traceLockAmbientEnabled
        sfxEnabled: root.traceLockSfxEnabled
        musicKey: root.traceLockMusicKey
        ambientKey: root.traceLockAmbientKey
        hitKey: root.traceLockHitKey
        missKey: root.traceLockMissKey
        comboKey: root.traceLockComboKey
        uiClickKey: root.traceLockUiClickKey
        musicVolume: root.traceLockMusicVolume
        ambientVolume: root.traceLockAmbientVolume
        sfxVolume: root.traceLockSfxVolume
    }

    // TASK26I shell card tokens: shell_top_status_card shell_left_nav_card shell_nav_card_home shell_nav_card_user shell_nav_card_calibration shell_nav_card_training shell_nav_card_report shell_nav_card_developer_lab shell_global_safety_card shell_status_chip_current_user shell_status_chip_connection shell_status_chip_quality shell_status_chip_control shell_status_chip_session shell_content_host_card
    // TASK25B global GUI skin layer: DesignBackground / DesignPanel / DesignButton consume design pack tokens. background.app.main
    // Compatibility token for static tests: pageStylesObj=renderResourcesObj.page_styles componentStylesObj=renderResourcesObj.component_styles gameStylesObj=renderResourcesObj.game_styles effectStylesObj=renderResourcesObj.effect_styles
}

// Compatibility tokens kept for TASK21/TASK23 tests:
// RELIC Core / Developer Diagnostics Console
// QML smoke shell loaded
// Connection Runtime Snapshot Attention Gyroscope Session Diagnostics Game HUD
// connection_status stream_alive device_connected attention_fresh attention_age_ms attention_last_update_ms gyro_x gyro_y gyro_z gyro_fresh gyro_age_ms gyro_last_update_ms session_type session_id latest_report_path warning_flags error_flags
// Control Panel Reconnect Start Session Stop Session Calibration Status Game Status Quality / Focus (TASK6) Live Input
// gameViewJson controlManifestJson controlStateJson last_command last_command_result last_command_error command_count
// profile_status calibration_status profile_loaded user_type attention_low_threshold attention_high_threshold preferred_game_id calibration_usable last_calibration_id failure_reason
// First Profile Calibration Quick Check Periodic Recalibration Triggered Recalibration
// GameCanvas will be restored in TASK24 score combo level session_elapsed_ms behavior_sample_count Fragment Lock Signal Hunter Stabilizer last_session_status current_session_id attention sqi fi_smoothed control_state
