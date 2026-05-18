import QtQuick

Rectangle {
    id: root

    property var gameView: ({})
    property var entities: (gameView && gameView.entities) ? gameView.entities : []
    property var visualEvents: (gameView && gameView.visual_events) ? gameView.visual_events : []
    property var guiBridgeRef: null
    property string fallbackGameId: "fake_game"
    property var designThemeObj: ({})
    property var gameStyleObj: ({})
    property var effectStyleObj: ({})

    color: styleValue(gameStyleObj.canvas || ({}), "background", "#1a1a1a")
    border.width: 1
    border.color: styleValue(gameStyleObj.canvas || ({}), "border", styleValue((designThemeObj.colors || ({})), "panel_border", "#888"))

    function styleValue(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function pxX(xNorm) {
        return Math.max(0, Math.min(width, xNorm * width))
    }

    function pxY(yNorm) {
        return Math.max(0, Math.min(height, yNorm * height))
    }

    function pxRadius(rNorm) {
        return Math.max(4, rNorm * Math.min(width, height))
    }

    function targetType(entity) {
        var md = entity && entity.metadata ? entity.metadata : ({})
        var t = md.target_type || entity.target_type || entity.role || "marked_trace"
        return String(t || "marked_trace")
    }

    function targetStyle(entity) {
        var targetRoot = gameStyleObj.target || ({})
        return targetRoot[targetType(entity)] || targetRoot.marked_trace || ({})
    }

    function targetFill(entity) {
        return styleValue(targetStyle(entity), "fill", "#f44")
    }

    function targetStroke(entity) {
        return styleValue(targetStyle(entity), "stroke", "#dddddd")
    }

    function targetGlow(entity) {
        return styleValue(targetStyle(entity), "glow", targetFill(entity))
    }

    function progressValue(entity) {
        var md = entity && entity.metadata ? entity.metadata : ({})
        var p = md.progress
        if (p === undefined || p === null) {
            p = md.remaining_lifetime_ratio
        }
        if (p === undefined || p === null) {
            return 0
        }
        return Math.max(0, Math.min(1, Number(p)))
    }

    function timerProgress() {
        var hud = gameView && gameView.hud ? gameView.hud : ({})
        var left = Number(hud.time_left_ms || 0)
        var total = Number(hud.game_duration_ms || 0)
        if (total <= 0) {
            return 0
        }
        return Math.max(0, Math.min(1, left / total))
    }

    function effectColor(effectType) {
        var e = effectStyleObj[effectType] || ({})
        return styleValue(e, "color", "#ffffff")
    }

    Rectangle {
        id: timerBack
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 8
        height: 6
        radius: 3
        color: styleValue(gameStyleObj.timer_bar || ({}), "background", "#374151")

        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: parent.width * root.timerProgress()
            radius: 3
            color: styleValue(gameStyleObj.timer_bar || ({}), "fill", "#F59E0B")
        }
    }

    Text {
        anchors.left: parent.left
        anchors.top: timerBack.bottom
        anchors.margins: 8
        color: styleValue(gameStyleObj.hud || ({}), "text_color", "#ddd")
        text: "GameCanvas | entities=" + root.entities.length + " | design_pack=active"
    }

    Repeater {
        model: root.entities
        delegate: Item {
            property var entity: modelData
            property real cx: root.pxX(entity.x || 0)
            property real cy: root.pxY(entity.y || 0)
            property real rr: root.pxRadius(entity.radius || 0)
            x: cx - rr
            y: cy - rr
            width: rr * 2
            height: rr * 2

            Rectangle {
                anchors.centerIn: parent
                width: parent.width + 18
                height: parent.height + 18
                radius: width / 2
                color: root.targetGlow(entity)
                opacity: entity.kind === "target" ? 0.18 : 0
                visible: entity.kind === "target"
            }

            Rectangle {
                anchors.fill: parent
                radius: width / 2
                color: entity.kind === "target" ? root.targetFill(entity) : (entity.kind === "focus_zone" ? "#44aaff33" : "transparent")
                border.width: entity.kind === "progress_ring" ? 3 : (entity.state === "active" ? 2 : 1)
                border.color: entity.kind === "progress_ring" ? styleValue(gameStyleObj.progress_ring || ({}), "stroke", "#ffdd55") : root.targetStroke(entity)
                visible: entity.kind === "target" || entity.kind === "focus_zone" || entity.kind === "progress_ring"
                opacity: entity.kind === "focus_zone" ? 0.45 : 1.0
            }

            Rectangle {
                anchors.centerIn: parent
                width: parent.width * root.progressValue(entity)
                height: Math.max(3, parent.height * 0.08)
                radius: height / 2
                color: styleValue(gameStyleObj.progress_ring || ({}), "background", "#1F2937")
                visible: entity.kind === "progress_ring"
            }

            Text {
                anchors.centerIn: parent
                color: styleValue(gameStyleObj.hud || ({}), "text_color", "#ddd")
                text: entity.kind === "progress_ring" ? ("P " + Math.round(root.progressValue(entity) * 100) + "%") : ""
                visible: entity.kind === "progress_ring"
                font.pixelSize: 11
            }
        }
    }

    Repeater {
        model: root.visualEvents
        delegate: Rectangle {
            property var eventObj: modelData
            property string effectType: String(eventObj.effect_type || eventObj.type || eventObj.kind || "trace_seal")
            width: 34
            height: 34
            radius: 17
            x: root.pxX(eventObj.x || 0.5) - width / 2
            y: root.pxY(eventObj.y || 0.5) - height / 2
            color: root.effectColor(effectType)
            opacity: 0.42
            border.width: 1
            border.color: "#ffffff"
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: function(mouse) {
            var xNorm = mouse.x / Math.max(1, root.width)
            var yNorm = mouse.y / Math.max(1, root.height)
            var payload = {
                "game_id": (root.gameView && root.gameView.game_id) ? root.gameView.game_id : root.fallbackGameId,
                "x_norm": xNorm,
                "y_norm": yNorm,
                "button": "left",
                "source": "game_canvas"
            }
            if (root.guiBridgeRef) {
                root.guiBridgeRef.sendEvent("pointer_click", JSON.stringify(payload))
            }
        }
    }
}
