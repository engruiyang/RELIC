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
    property var renderResourcesObj: ({})

    color: styleValue(gameStyleObj.canvas || ({}), "background_color", "#1a1a1a")
    radius: Number(styleValue(gameStyleObj.canvas || ({}), "radius", 0))
    border.width: 1
    border.color: styleValue(gameStyleObj.canvas || ({}), "border", styleValue((designThemeObj.colors || ({})), "panel_border", "#888"))

    DesignBackground {
        anchors.fill: parent
        themeObj: root.designThemeObj
        styleObj: ({"background": (root.gameStyleObj.canvas || ({})).background || (root.gameStyleObj.canvas || ({})).background_color || "#1a1a1a"})
        renderResourcesObj: root.renderResourcesObj
        fallbackColor: root.styleValue(root.gameStyleObj.canvas || ({}), "background_color", "#1a1a1a")
    }

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

    function effectStyle(effectType) {
        return effectStyleObj[effectType] || ({})
    }

    function effectColor(effectType) {
        var e = effectStyle(effectType)
        return styleValue(e, "color", "#ffffff")
    }

    function effectGlow(effectType) {
        var e = effectStyle(effectType)
        return styleValue(e, "glow", effectColor(effectType))
    }

    function effectDuration(effectType) {
        var e = effectStyle(effectType)
        return Number(styleValue(e, "duration_ms", 320))
    }

    function effectTypeName(effectType) {
        var e = effectStyle(effectType)
        return String(styleValue(e, "type", effectType))
    }

    function effectParticleCount(effectType) {
        var e = effectStyle(effectType)
        return Math.max(0, Number(styleValue(e, "particle_count", 0)))
    }

    function effectScaleFrom(effectType) {
        var e = effectStyle(effectType)
        return Number(styleValue(e, "scale_from", 0.7))
    }

    function effectScaleTo(effectType) {
        var e = effectStyle(effectType)
        return Number(styleValue(e, "scale_to", 1.45))
    }

    function effectOpacityFrom(effectType) {
        var e = effectStyle(effectType)
        return Number(styleValue(e, "opacity_from", 0.82))
    }

    function effectOpacityTo(effectType) {
        var e = effectStyle(effectType)
        return Number(styleValue(e, "opacity_to", 0.0))
    }

    function effectRadius(effectType) {
        var e = effectStyle(effectType)
        return Number(styleValue(e, "radius", 34))
    }

    function effectLabel(effectType) {
        if (effectType === "combo_popup") {
            return "COMBO"
        }
        if (effectType === "lock_failed") {
            return "MISS"
        }
        if (effectType === "trace_drop") {
            return "DROP"
        }
        return "HIT"
    }

    function normalizedImageUrl(rawUrl) {
        if (rawUrl === undefined || rawUrl === null || rawUrl === "") {
            return ""
        }
        var u = String(rawUrl)
        if (u.indexOf("placeholder://") === 0) {
            return ""
        }
        if (u.indexOf("file:") === 0 || u.indexOf("qrc:") === 0 || u.indexOf("http:") === 0 || u.indexOf("https:") === 0 || u.indexOf("/") === 0) {
            return u
        }
        return Qt.resolvedUrl("../../assets/" + u)
    }

    function assetDescriptor(assetKey) {
        if (assetKey === undefined || assetKey === null || assetKey === "") {
            return ({})
        }
        var assets = renderResourcesObj.assets || ({})
        return assets[String(assetKey)] || ({})
    }

    function targetAssetKey(entity) {
        var s = targetStyle(entity)
        var key = entity && entity.asset_key ? entity.asset_key : ""
        if (key === "") {
            key = styleValue(s, "asset_key", "")
        }
        return key
    }

    function targetAssetDescriptor(entity) {
        return assetDescriptor(targetAssetKey(entity))
    }

    function targetImageSource(entity) {
        var desc = targetAssetDescriptor(entity)
        var style = targetStyle(entity)
        return normalizedImageUrl(desc.url || styleValue(style, "url", ""))
    }

    function targetFallbackShape(entity) {
        var desc = targetAssetDescriptor(entity)
        var style = targetStyle(entity)
        return String(desc.fallback_shape || styleValue(style, "fallback_shape", "circle"))
    }

    function isTargetImageAvailable(entity) {
        return targetImageSource(entity) !== ""
    }

    Rectangle {
        id: timerBack
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 8
        height: Number(styleValue(gameStyleObj.timer_bar || ({}), "height", 6))
        radius: height / 2
        color: styleValue(gameStyleObj.timer_bar || ({}), "background", "#374151")

        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: parent.width * root.timerProgress()
            radius: height / 2
            color: styleValue(gameStyleObj.timer_bar || ({}), "fill", "#F59E0B")
        }
    }

    Text {
        anchors.left: parent.left
        anchors.top: timerBack.bottom
        anchors.margins: 8
        color: styleValue(gameStyleObj.hud || ({}), "text_color", "#ddd")
        text: "GameCanvas | entities=" + root.entities.length + " | design_pack=active | background/target image asset_key supported"
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

            Image {
                anchors.fill: parent
                source: root.targetImageSource(entity)
                visible: entity.kind === "target" && root.isTargetImageAvailable(entity)
                fillMode: Image.PreserveAspectFit
                smooth: true
                mipmap: true
            }

            Rectangle {
                anchors.fill: parent
                radius: root.targetFallbackShape(entity) === "circle" ? width / 2 : Math.max(2, width * 0.12)
                rotation: root.targetFallbackShape(entity) === "diamond" ? 45 : 0
                color: entity.kind === "target" ? root.targetFill(entity) : (entity.kind === "focus_zone" ? "#44aaff33" : "transparent")
                border.width: entity.kind === "progress_ring" ? Number(styleValue(gameStyleObj.progress_ring || ({}), "width", 3)) : (entity.state === "active" ? 2 : 1)
                border.color: entity.kind === "progress_ring" ? styleValue(gameStyleObj.progress_ring || ({}), "stroke", "#ffdd55") : root.targetStroke(entity)
                visible: (entity.kind === "target" && !root.isTargetImageAvailable(entity)) || entity.kind === "focus_zone" || entity.kind === "progress_ring"
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
        delegate: Item {
            id: effectRoot
            property var eventObj: modelData
            property string effectType: String(eventObj.effect_type || eventObj.type || eventObj.kind || "trace_seal")
            property string effectKind: root.effectTypeName(effectType)
            property real baseSize: root.effectRadius(effectType)
            property int durationMs: root.effectDuration(effectType)
            property real startScale: root.effectScaleFrom(effectType)
            property real endScale: root.effectScaleTo(effectType)
            property real startOpacity: root.effectOpacityFrom(effectType)
            property real endOpacity: root.effectOpacityTo(effectType)

            width: baseSize
            height: baseSize
            x: root.pxX(eventObj.x || 0.5) - width / 2
            y: root.pxY(eventObj.y || 0.5) - height / 2
            opacity: startOpacity
            scale: startScale

            Rectangle {
                id: effectHalo
                anchors.fill: parent
                radius: width / 2
                color: root.effectColor(effectRoot.effectType)
                opacity: effectRoot.effectKind === "flash" ? 0.54 : 0.28
                border.width: effectRoot.effectKind === "fade" ? 1 : 2
                border.color: root.effectGlow(effectRoot.effectType)
            }

            Text {
                anchors.centerIn: parent
                visible: effectRoot.effectType === "combo_popup" || effectRoot.effectKind === "popup"
                text: root.effectLabel(effectRoot.effectType)
                color: root.effectGlow(effectRoot.effectType)
                font.bold: true
                font.pixelSize: 12
            }

            Repeater {
                model: root.effectParticleCount(effectRoot.effectType)
                delegate: Rectangle {
                    property real angle: (index / Math.max(1, root.effectParticleCount(effectRoot.effectType))) * Math.PI * 2
                    property real distance: effectRoot.baseSize * 0.72
                    width: 5
                    height: 5
                    radius: 2.5
                    x: effectRoot.width / 2 + Math.cos(angle) * distance - width / 2
                    y: effectRoot.height / 2 + Math.sin(angle) * distance - height / 2
                    color: root.effectColor(effectRoot.effectType)
                    opacity: 0.72
                    visible: effectRoot.effectKind === "particle_burst" || effectRoot.effectKind === "burst" || root.effectParticleCount(effectRoot.effectType) > 0
                }
            }

            NumberAnimation on scale {
                from: effectRoot.startScale
                to: effectRoot.endScale
                duration: effectRoot.durationMs
                easing.type: Easing.OutCubic
                running: true
            }

            NumberAnimation on opacity {
                from: effectRoot.startOpacity
                to: effectRoot.endOpacity
                duration: effectRoot.durationMs
                easing.type: Easing.OutCubic
                running: true
            }
        }
    }

    // TASK25B GameCanvas consumes canvas.background layered color/image/gradient/overlay and TraceLock game style tokens.
    // TASK25C GameCanvas consumes TraceLock visual asset_key/style_key tokens.
    // canvas.background layered color/image/gradient/overlay
    // TASK25D effect_styles parameterize trace_seal lock_failed trace_drop combo_popup pulse flash fade popup simple burst particle_burst duration_ms color particle_count scale_from scale_to opacity_from opacity_to
    // targetAssetKey targetAssetDescriptor targetImageSource targetFallbackShape isTargetImageAvailable asset_key fallback_shape Image {

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
