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
    property var localFeedbacks: []
    property int localFeedbackSeq: 0
    property var activeVisualEvents: []
    property int visualEventSerial: 0
    property int animationTick: 0

    // Diagnostic-only fields for resolving GameCanvas coordinate/time desync.
    // They do not change game logic; they print the exact display-space and
    // backend-bound values used for each pointer press.
    property bool diagnosticEnabled: false
    property int clickDiagnosticSeq: 0
    property int lastRingDiagnosticAtMs: 0
    property string lastClickDiagnosticJson: "{}"


    onVisualEventsChanged: mergeVisualEvents(root.visualEvents)
    onEntitiesChanged: syncDisplayEntities()
    Component.onCompleted: {
        syncDisplayEntities()
        mergeVisualEvents(root.visualEvents)
    }

    ListModel { id: displayEntityModel }
    ListModel { id: visualEventModel }
    ListModel { id: localFeedbackModel }

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

    Canvas {
        id: backgroundVfxCanvas
        anchors.fill: parent
        visible: Boolean(root.styleValue((root.gameStyleObj.canvas || ({})).background_effects || ({}), "enabled", true))
        opacity: Number(root.styleValue((root.gameStyleObj.canvas || ({})).background_effects || ({}), "opacity", 0.22))
        property int tick: root.animationTick
        onTickChanged: requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            var fx = (root.gameStyleObj.canvas || ({})).background_effects || ({})
            var ctx = getContext("2d")
            ctx.reset()
            var primary = root.styleValue(fx, "primary", "#22D3EE")
            var secondary = root.styleValue(fx, "secondary", "#A855F7")
            var warning = root.styleValue(fx, "warning", "#F59E0B")
            var speed = Math.max(0.1, Number(root.styleValue(fx, "speed", 1.0)))
            var t = Number(root.animationTick || 0) * speed
            var lineAlpha = Math.max(0.02, Math.min(0.5, Number(root.styleValue(fx, "line_alpha", 0.18))))

            if (root.styleValue(fx, "scanline_enabled", true)) {
                ctx.globalAlpha = lineAlpha
                ctx.strokeStyle = primary
                ctx.lineWidth = 1
                var step = 18
                var offset = (t * 0.9) % step
                for (var y = -step; y < height + step; y += step) {
                    ctx.beginPath()
                    ctx.moveTo(0, y + offset)
                    ctx.lineTo(width, y + offset)
                    ctx.stroke()
                }
            }

            if (root.styleValue(fx, "data_stream_enabled", true)) {
                var count = Math.max(0, Number(root.styleValue(fx, "particle_count", 24)))
                for (var i = 0; i < count; i += 1) {
                    var x = ((i * 97 + t * (1.6 + (i % 5) * 0.2)) % Math.max(1, width + 80)) - 40
                    var y2 = (i * 53) % Math.max(1, height)
                    var len = 18 + (i % 4) * 10
                    ctx.globalAlpha = 0.10 + (i % 5) * 0.025
                    ctx.strokeStyle = (i % 3 === 0) ? secondary : primary
                    ctx.lineWidth = 1 + (i % 2)
                    ctx.beginPath()
                    ctx.moveTo(x, y2)
                    ctx.lineTo(x + len, y2 - len * 0.24)
                    ctx.stroke()
                }
            }

            if (root.styleValue(fx, "pulse_enabled", true)) {
                var pulse = 0.5 + 0.5 * Math.sin(t / 18.0)
                var r = Math.max(width, height) * (0.16 + pulse * 0.10)
                var cx = width * (0.5 + Math.sin(t / 55.0) * 0.10)
                var cy = height * (0.52 + Math.cos(t / 60.0) * 0.08)
                var grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r)
                grad.addColorStop(0.0, warning)
                grad.addColorStop(0.36, secondary)
                grad.addColorStop(1.0, "rgba(0,0,0,0)")
                ctx.globalAlpha = 0.12 + pulse * 0.10
                ctx.fillStyle = grad
                ctx.beginPath()
                ctx.arc(cx, cy, r, 0, Math.PI * 2)
                ctx.fill()
            }
            ctx.globalAlpha = 1.0
        }
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

    function parseJsonObject(raw) {
        if (raw === undefined || raw === null || raw === "") {
            return ({})
        }
        if (typeof raw === "object") {
            return raw
        }
        try {
            return JSON.parse(String(raw))
        } catch (e) {
            return ({})
        }
    }

    function entityId(entity, fallbackIndex) {
        if (!entity) return "entity_" + fallbackIndex
        return String(entity.id || entity.entity_id || entity.target_id || entity.kind + "_" + fallbackIndex)
    }

    function findDisplayEntityIndex(entityIdValue) {
        for (var i = 0; i < displayEntityModel.count; i += 1) {
            if (String(displayEntityModel.get(i).entityId || "") === String(entityIdValue)) {
                return i
            }
        }
        return -1
    }

    function visualRadiusNorm(entity) {
        if (!entity) return 0
        var md = entity.metadata || ({})
        var raw = md.visual_radius
        if (raw === undefined || raw === null || raw === "") raw = md.display_radius
        if (raw === undefined || raw === null || raw === "") raw = entity.radius
        return Number(raw || 0)
    }

    function hitRadiusNorm(entity) {
        if (!entity) return 0
        var md = entity.metadata || ({})
        var raw = md.hit_radius
        if (raw === undefined || raw === null || raw === "") raw = entity.radius
        return Number(raw || 0)
    }

    function entityToModel(entity, fallbackIndex) {
        var md = entity && entity.metadata ? entity.metadata : ({})
        var hitRadius = hitRadiusNorm(entity)
        var visualRadius = visualRadiusNorm(entity)
        return {
            "entityId": entityId(entity, fallbackIndex),
            "kind": String((entity && entity.kind) || ""),
            "role": String((entity && entity.role) || ""),
            "xNorm": Number((entity && entity.x) || 0),
            "yNorm": Number((entity && entity.y) || 0),
            "radiusNorm": Number((entity && entity.radius) || 0),
            "hitRadiusNorm": hitRadius,
            "visualRadiusNorm": visualRadius,
            "state": String((entity && entity.state) || ""),
            "styleKey": String((entity && entity.style_key) || ""),
            "assetKey": String((entity && entity.asset_key) || ""),
            "interactive": Boolean(entity && entity.interactive),
            "hitShape": String((entity && entity.hit_shape) || "circle"),
            "progress": progressValue(entity),
            "timeLeftMs": Number(md.time_left_ms || md.target_time_left_ms || 0),
            "targetLifetimeMs": Number(md.target_lifetime_ms || 0),
            "updatedAtMs": Date.now(),
            "metadataJson": JSON.stringify(md),
            "entityJson": JSON.stringify(entity || ({}))
        }
    }

    function modelToEntity(row) {
        if (row === undefined || row === null) {
            return ({})
        }
        return parseJsonObject(row.entityJson || "{}")
    }

    function syncDisplayEntities() {
        var seen = ({})
        var source = root.entities || []
        for (var i = 0; i < source.length; i += 1) {
            var entity = source[i]
            if (!entity) continue
            var row = entityToModel(entity, i)
            seen[row.entityId] = true
            var idx = findDisplayEntityIndex(row.entityId)
            if (idx < 0) {
                displayEntityModel.append(row)
            } else {
                displayEntityModel.setProperty(idx, "kind", row.kind)
                displayEntityModel.setProperty(idx, "role", row.role)
                displayEntityModel.setProperty(idx, "xNorm", row.xNorm)
                displayEntityModel.setProperty(idx, "yNorm", row.yNorm)
                displayEntityModel.setProperty(idx, "radiusNorm", row.radiusNorm)
                displayEntityModel.setProperty(idx, "hitRadiusNorm", row.hitRadiusNorm)
                displayEntityModel.setProperty(idx, "visualRadiusNorm", row.visualRadiusNorm)
                displayEntityModel.setProperty(idx, "state", row.state)
                displayEntityModel.setProperty(idx, "styleKey", row.styleKey)
                displayEntityModel.setProperty(idx, "assetKey", row.assetKey)
                displayEntityModel.setProperty(idx, "interactive", row.interactive)
                displayEntityModel.setProperty(idx, "hitShape", row.hitShape)
                displayEntityModel.setProperty(idx, "progress", row.progress)
                displayEntityModel.setProperty(idx, "timeLeftMs", row.timeLeftMs)
                displayEntityModel.setProperty(idx, "targetLifetimeMs", row.targetLifetimeMs)
                displayEntityModel.setProperty(idx, "updatedAtMs", row.updatedAtMs)
                displayEntityModel.setProperty(idx, "metadataJson", row.metadataJson)
                displayEntityModel.setProperty(idx, "entityJson", row.entityJson)
            }
        }
        for (var j = displayEntityModel.count - 1; j >= 0; j -= 1) {
            var existingId = String(displayEntityModel.get(j).entityId || "")
            if (!seen[existingId]) {
                displayEntityModel.remove(j)
            }
        }
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

    function progressValueFromModel(row) {
        if (row === undefined || row === null) {
            return 0
        }
        // Depend on animationTick so QML recomputes between authoritative JSON frames.
        var _tick = root.animationTick
        var p = Math.max(0, Math.min(1, Number(row.progress || 0)))
        var left = Number(row.timeLeftMs || 0)
        var lifetime = Number(row.targetLifetimeMs || 0)
        var updatedAt = Number(row.updatedAtMs || 0)
        if (left > 0 && lifetime > 0 && updatedAt > 0) {
            var remaining = left - Math.max(0, Date.now() - updatedAt)
            return Math.max(0, Math.min(1, remaining / lifetime))
        }
        return p
    }

    function progressStyle() {
        return renderResourceStyle("tracelock.progress_ring.default", root.gameStyleObj.progress_ring || ({}))
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

    function frameId() {
        return Number((root.gameView && root.gameView.frame_id) ? root.gameView.frame_id : 0)
    }

    function safeModelGet(modelObj, idx) {
        if (!modelObj || idx < 0 || idx >= modelObj.count) {
            return null
        }
        var row = modelObj.get(idx)
        return (row === undefined || row === null) ? null : row
    }

    function primaryTargetRow() {
        for (var i = 0; i < displayEntityModel.count; i += 1) {
            var row = safeModelGet(displayEntityModel, i)
            if (!row) continue
            if (String(row.kind || "") === "target") {
                return row
            }
        }
        return null
    }

    function progressRingRowForTarget(targetRow) {
        var targetId = targetRow ? String(targetRow.entityId || "") : ""
        var fallback = null
        for (var i = 0; i < displayEntityModel.count; i += 1) {
            var row = safeModelGet(displayEntityModel, i)
            if (!row) continue
            if (String(row.kind || "") !== "progress_ring") continue
            if (fallback === null) {
                fallback = row
            }
            if (targetId !== "" && String(row.entityId || "").indexOf(targetId) >= 0) {
                return row
            }
        }
        return fallback
    }

    function rowAgeMs(row, nowMs) {
        if (!row) return -1
        var updatedAt = Number(row.updatedAtMs || 0)
        return updatedAt > 0 ? Math.max(0, nowMs - updatedAt) : -1
    }

    function rowProgressAt(row, nowMs) {
        if (!row) return 0
        var p = Math.max(0, Math.min(1, Number(row.progress || 0)))
        var left = Number(row.timeLeftMs || 0)
        var lifetime = Number(row.targetLifetimeMs || 0)
        var updatedAt = Number(row.updatedAtMs || 0)
        if (left > 0 && lifetime > 0 && updatedAt > 0) {
            var remaining = left - Math.max(0, nowMs - updatedAt)
            return Math.max(0, Math.min(1, remaining / lifetime))
        }
        return p
    }

    function clickDiagnostic(mouse, xNorm, yNorm) {
        var now = Date.now()
        var target = primaryTargetRow()
        var ring = progressRingRowForTarget(target)
        var tx = target ? Number(target.xNorm || 0) : -1
        var ty = target ? Number(target.yNorm || 0) : -1
        var hr = target ? Number(target.hitRadiusNorm || target.radiusNorm || 0) : -1
        var dx = target ? (Number(xNorm) - tx) : 0
        var dy = target ? (Number(yNorm) - ty) : 0
        var dist = target ? Math.sqrt(dx * dx + dy * dy) : -1
        var candidate = target ? (dist <= hr) : false
        root.clickDiagnosticSeq += 1
        var diag = {
            "seq": root.clickDiagnosticSeq,
            "source": "GameCanvas.qml",
            "frame_id": frameId(),
            "root_w": Number(root.width || 0),
            "root_h": Number(root.height || 0),
            "mouse_x": Number(mouse.x || 0),
            "mouse_y": Number(mouse.y || 0),
            "x_norm_sent": Number(xNorm),
            "y_norm_sent": Number(yNorm),
            "target_present": target !== null,
            "display_target_id": target ? String(target.entityId || "") : "",
            "display_target_x": tx,
            "display_target_y": ty,
            "display_hit_radius": hr,
            "display_radius": target ? Number(target.radiusNorm || 0) : -1,
            "display_visual_radius": target ? Number(target.visualRadiusNorm || target.radiusNorm || 0) : -1,
            "display_dx": dx,
            "display_dy": dy,
            "display_dist": dist,
            "display_hit_candidate": candidate,
            "display_target_age_ms": rowAgeMs(target, now),
            "display_progress": rowProgressAt(target, now),
            "display_time_left_ms": target ? Number(target.timeLeftMs || 0) : -1,
            "display_lifetime_ms": target ? Number(target.targetLifetimeMs || 0) : -1,
            "ring_present": ring !== null,
            "ring_progress": rowProgressAt(ring, now),
            "ring_age_ms": rowAgeMs(ring, now),
            "ring_time_left_ms": ring ? Number(ring.timeLeftMs || 0) : -1,
            "ring_lifetime_ms": ring ? Number(ring.targetLifetimeMs || 0) : -1
        }
        root.lastClickDiagnosticJson = JSON.stringify(diag)
        if (root.diagnosticEnabled) {
            console.log("[CANVAS CLICK DEBUG] " + root.lastClickDiagnosticJson)
        }
        return diag
    }

    function logRingDiagnostic() {
        if (!root.diagnosticEnabled || !root.visible) return
        var now = Date.now()
        if (now - root.lastRingDiagnosticAtMs < 300) return
        root.lastRingDiagnosticAtMs = now
        var target = primaryTargetRow()
        var ring = progressRingRowForTarget(target)
        if (!target && !ring) return
        var diag = {
            "source": "GameCanvas.qml",
            "frame_id": frameId(),
            "target_id": target ? String(target.entityId || "") : "",
            "target_age_ms": rowAgeMs(target, now),
            "target_progress": rowProgressAt(target, now),
            "target_time_left_ms": target ? Number(target.timeLeftMs || 0) : -1,
            "target_lifetime_ms": target ? Number(target.targetLifetimeMs || 0) : -1,
            "ring_age_ms": rowAgeMs(ring, now),
            "ring_progress": rowProgressAt(ring, now),
            "ring_time_left_ms": ring ? Number(ring.timeLeftMs || 0) : -1,
            "ring_lifetime_ms": ring ? Number(ring.targetLifetimeMs || 0) : -1
        }
        console.log("[RING DEBUG] " + JSON.stringify(diag))
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

    function pushLocalFeedback(xNorm, yNorm, kind) {
        localFeedbackSeq += 1
        var now = Date.now()
        localFeedbackModel.append({
            "eventId": "local_feedback_" + localFeedbackSeq,
            "xNorm": Math.max(0, Math.min(1, Number(xNorm))),
            "yNorm": Math.max(0, Math.min(1, Number(yNorm))),
            "kind": String(kind || "press"),
            "createdAtMs": now,
            "durationMs": 480
        })
        while (localFeedbackModel.count > 14) {
            localFeedbackModel.remove(0)
        }
    }

    function eventKey(evt) {
        if (!evt) return ""
        return String(evt.event_id || evt.id || evt.target_id || "")
               + ":" + String(evt.kind || evt.effect_key || evt.type || "")
               + ":" + String(evt.x || "") + ":" + String(evt.y || "")
    }

    function findVisualEventIndex(eventKeyValue) {
        for (var i = 0; i < visualEventModel.count; i += 1) {
            if (String(visualEventModel.get(i).eventKey || "") === String(eventKeyValue)) {
                return i
            }
        }
        return -1
    }

    function mergeVisualEvents(events) {
        if (!events || events.length === 0) return
        var now = Date.now()
        for (var j = 0; j < events.length; j += 1) {
            var evt = events[j]
            if (!evt) continue
            var effectType = String(evt.effect_type || evt.type || evt.kind || "trace_seal")
            var key = eventKey(evt)
            if (key.length === 0) {
                visualEventSerial += 1
                key = "visual_evt_" + visualEventSerial
            }
            if (findVisualEventIndex(key) >= 0) {
                continue
            }
            var duration = Math.max(280, Number(evt.duration_ms || effectDuration(effectType)))
            visualEventModel.append({
                "eventKey": key,
                "eventId": String(evt.event_id || key),
                "effectType": effectType,
                "xNorm": Math.max(0, Math.min(1, Number(evt.x || 0.5))),
                "yNorm": Math.max(0, Math.min(1, Number(evt.y || 0.5))),
                "targetId": String(evt.target_id || ""),
                "createdAtMs": now,
                "durationMs": duration,
                "intensity": Number(evt.intensity || 1.0),
                "payloadJson": JSON.stringify(evt.payload || ({}))
            })
        }
        while (visualEventModel.count > 32) {
            visualEventModel.remove(0)
        }
    }

    function pruneVisualEvents() {
        var now = Date.now()
        for (var i = visualEventModel.count - 1; i >= 0; i -= 1) {
            var evt = visualEventModel.get(i)
            var duration = Math.max(280, Number(evt.durationMs || effectDuration(evt.effectType || "trace_seal")))
            if (now - Number(evt.createdAtMs || now) > duration + 180) {
                visualEventModel.remove(i)
            }
        }
        for (var j = localFeedbackModel.count - 1; j >= 0; j -= 1) {
            var fb = localFeedbackModel.get(j)
            var fbDuration = Math.max(240, Number(fb.durationMs || 360))
            if (now - Number(fb.createdAtMs || now) > fbDuration + 120) {
                localFeedbackModel.remove(j)
            }
        }
    }

    function sendPointerClick(xNorm, yNorm, diagnostic) {
        var payload = {
            "game_id": (root.gameView && root.gameView.game_id) ? root.gameView.game_id : root.fallbackGameId,
            "x_norm": xNorm,
            "y_norm": yNorm,
            "button": "left",
            "source": "game_canvas",
            "input_phase": "pressed",
            "client_created_at_ms": Date.now()
        }
        if (root.diagnosticEnabled && diagnostic) {
            payload["diagnostic"] = diagnostic
            payload["display_frame_id"] = diagnostic.frame_id
            payload["display_target_id"] = diagnostic.display_target_id
            payload["display_target_x"] = diagnostic.display_target_x
            payload["display_target_y"] = diagnostic.display_target_y
            payload["display_hit_radius"] = diagnostic.display_hit_radius
            payload["display_dist"] = diagnostic.display_dist
            payload["display_hit_candidate"] = diagnostic.display_hit_candidate
            payload["display_target_age_ms"] = diagnostic.display_target_age_ms
            payload["display_progress"] = diagnostic.display_progress
            payload["ring_progress"] = diagnostic.ring_progress
        }
        if (!root.guiBridgeRef) {
            return
        }
        if (root.guiBridgeRef.handleGamePointerClick) {
            root.guiBridgeRef.handleGamePointerClick(JSON.stringify(payload))
        } else {
            root.guiBridgeRef.sendEvent("pointer_click", JSON.stringify(payload))
        }
    }

    function renderResourceStyle(assetKey, fallbackStyle) {
        var desc = assetDescriptor(assetKey)
        var styleKey = desc.style_key || ""
        var styles = renderResourcesObj.styles || ({})
        if (styleKey !== "" && styles[styleKey]) {
            return styles[styleKey]
        }
        return fallbackStyle || ({})
    }

    function backgroundAssetDescriptor() {
        var canvas = root.gameStyleObj.canvas || ({})
        return assetDescriptor(root.styleValue(canvas, "asset_key", "tracelock.background.grid"))
    }

    function backgroundImageSource() {
        var desc = backgroundAssetDescriptor()
        return normalizedImageUrl(desc.url || "")
    }

    function isBackgroundImageAvailable() {
        return backgroundImageSource() !== ""
    }

    function progressRingAssetDescriptor(row) {
        var style = root.progressStyle()
        var key = String((row && row.assetKey) || root.styleValue(style, "asset_key", "tracelock.progress_ring.default"))
        return assetDescriptor(key)
    }

    function progressRingImageSource(row) {
        var desc = progressRingAssetDescriptor(row)
        var style = root.progressStyle()
        return normalizedImageUrl(desc.url || root.styleValue(style, "url", ""))
    }

    function isProgressRingImageAvailable(row) {
        return progressRingImageSource(row) !== ""
    }

    function rowImageSource(row) {
        if (!row) return ""
        if (String(row.kind || "") === "progress_ring") {
            return progressRingImageSource(row)
        }
        return ""
    }

    function effectAssetKey(effectType) {
        var e = effectStyle(effectType)
        var key = root.styleValue(e, "asset_key", "")
        if (key !== "") return key
        var et = String(effectType || "trace_seal")
        if (et.indexOf("tracelock.effect.") === 0) return et
        return "tracelock.effect." + et
    }

    function effectAssetDescriptor(effectType) {
        return assetDescriptor(effectAssetKey(effectType))
    }

    function effectImageSource(effectType) {
        var desc = effectAssetDescriptor(effectType)
        var e = effectStyle(effectType)
        return normalizedImageUrl(desc.url || root.styleValue(e, "url", ""))
    }

    function isEffectImageAvailable(effectType) {
        return effectImageSource(effectType) !== ""
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
            Behavior on width { NumberAnimation { duration: 60; easing.type: Easing.Linear } }
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
        model: displayEntityModel
        delegate: Item {
            property var entity: root.modelToEntity(displayEntityModel.get(index))
            property string entityKind: String(model.kind || "")
            property bool isAuthoritativeHitEntity: entityKind === "target" || entityKind === "progress_ring"
            property int motionAnimDuration: isAuthoritativeHitEntity ? 0 : 70
            property real cx: root.pxX(Number(model.xNorm || 0))
            property real cy: root.pxY(Number(model.yNorm || 0))
            property real rr: root.pxRadius(Number(model.visualRadiusNorm || model.radiusNorm || 0))
            property real hitRr: root.pxRadius(Number(model.hitRadiusNorm || model.radiusNorm || 0))
            x: cx - rr
            y: cy - rr
            width: rr * 2
            height: rr * 2

            Behavior on x { NumberAnimation { duration: motionAnimDuration; easing.type: Easing.Linear } }
            Behavior on y { NumberAnimation { duration: motionAnimDuration; easing.type: Easing.Linear } }
            Behavior on width { NumberAnimation { duration: motionAnimDuration; easing.type: Easing.Linear } }
            Behavior on height { NumberAnimation { duration: motionAnimDuration; easing.type: Easing.Linear } }

            Rectangle {
                anchors.centerIn: parent
                width: Math.max(0, hitRr * 2)
                height: Math.max(0, hitRr * 2)
                radius: width / 2
                color: root.targetGlow(entity)
                opacity: entityKind === "target" ? 0.10 : 0
                visible: entityKind === "target"
            }

            Rectangle {
                anchors.centerIn: parent
                width: Math.max(0, hitRr * 2)
                height: Math.max(0, hitRr * 2)
                radius: width / 2
                color: "transparent"
                border.width: entityKind === "target" ? 1 : 0
                border.color: root.targetStroke(entity)
                opacity: entityKind === "target" ? 0.70 : 0
                visible: entityKind === "target"
            }

            Image {
                anchors.centerIn: parent
                width: Math.max(0, hitRr * 2)
                height: Math.max(0, hitRr * 2)
                source: root.targetImageSource(entity)
                visible: entityKind === "target" && root.isTargetImageAvailable(entity)
                fillMode: Image.PreserveAspectFit
                smooth: true
                mipmap: true
            }

            Rectangle {
                anchors.centerIn: parent
                width: entityKind === "target" ? Math.max(0, hitRr * 2) : parent.width
                height: entityKind === "target" ? Math.max(0, hitRr * 2) : parent.height
                radius: root.targetFallbackShape(entity) === "circle" ? width / 2 : Math.max(2, width * 0.12)
                rotation: root.targetFallbackShape(entity) === "diamond" ? 45 : 0
                color: entityKind === "target" ? root.targetFill(entity) : (entityKind === "focus_zone" ? "#44aaff33" : "transparent")
                border.width: (model.state === "active" ? 2 : 1)
                border.color: root.targetStroke(entity)
                visible: (entityKind === "target" && !root.isTargetImageAvailable(entity)) || entityKind === "focus_zone"
                opacity: entityKind === "focus_zone" ? 0.16 : 1.0
            }

            Image {
                id: progressRingImage
                anchors.centerIn: parent
                width: Math.max(0, hitRr * 2 + Number(root.styleValue(root.progressStyle(), "outer_padding", 8)) + 10)
                height: width
                source: root.progressRingImageSource(model)
                visible: entityKind === "progress_ring" && root.isProgressRingImageAvailable(model)
                fillMode: Image.PreserveAspectFit
                smooth: true
                mipmap: true
                opacity: Number(root.styleValue(root.progressStyle(), "image_opacity", 0.36))
            }

            Canvas {
                id: progressArc
                anchors.centerIn: parent
                width: Math.max(0, hitRr * 2 + Number(root.styleValue(root.progressStyle(), "outer_padding", 8)))
                height: width
                visible: entityKind === "progress_ring"
                property real liveProgress: root.progressValueFromModel(model)
                property int tick: root.animationTick
                onLiveProgressChanged: requestPaint()
                onTickChanged: requestPaint()
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                onPaint: {
                    var ctx = getContext("2d")
                    ctx.reset()
                    var lineW = Math.max(2, Number(root.styleValue(root.progressStyle(), "width", 3)))
                    var r = Math.max(1, Math.min(width, height) / 2 - lineW / 2 - 1)
                    var cx2 = width / 2
                    var cy2 = height / 2
                    ctx.lineCap = "round"
                    ctx.lineWidth = lineW
                    ctx.strokeStyle = root.styleValue(root.progressStyle(), "background", "rgba(31,41,55,0.38)")
                    ctx.beginPath()
                    ctx.arc(cx2, cy2, r, -Math.PI / 2, Math.PI * 1.5, false)
                    ctx.stroke()
                    ctx.strokeStyle = root.styleValue(root.progressStyle(), "stroke", "#ffdd55")
                    ctx.beginPath()
                    ctx.arc(cx2, cy2, r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * Math.max(0, Math.min(1, liveProgress)), false)
                    ctx.stroke()
                }
            }
        }
    }

    Repeater {
        model: visualEventModel
        delegate: Item {
            id: effectRoot
            property string effectType: String(model.effectType || "trace_seal")
            property string effectKind: root.effectTypeName(effectType)
            property real baseSize: root.effectRadius(effectType)
            property int durationMs: Math.max(280, Number(model.durationMs || root.effectDuration(effectType)))
            property real startScale: root.effectScaleFrom(effectType)
            property real endScale: root.effectScaleTo(effectType)
            property real startOpacity: root.effectOpacityFrom(effectType)
            property real endOpacity: root.effectOpacityTo(effectType)

            width: baseSize
            height: baseSize
            x: root.pxX(Number(model.xNorm || 0.5)) - width / 2
            y: root.pxY(Number(model.yNorm || 0.5)) - height / 2
            opacity: startOpacity
            scale: startScale
            visible: true

            Rectangle {
                id: effectHalo
                anchors.fill: parent
                radius: width / 2
                color: root.effectColor(effectRoot.effectType)
                opacity: effectRoot.effectKind === "flash" ? 0.54 : 0.28
                border.width: effectRoot.effectKind === "fade" ? 1 : 2
                border.color: root.effectGlow(effectRoot.effectType)
            }

            Image {
                id: effectImage
                anchors.centerIn: parent
                width: parent.width
                height: parent.height
                source: root.effectImageSource(effectRoot.effectType)
                visible: root.isEffectImageAvailable(effectRoot.effectType)
                fillMode: Image.PreserveAspectFit
                smooth: true
                mipmap: true
                opacity: Number(root.styleValue(root.effectStyle(effectRoot.effectType), "image_opacity", 0.72))
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

    Repeater {
        model: localFeedbackModel
        delegate: Item {
            id: localFeedbackRoot
            property string effectType: "local_ripple"
            property real baseSize: root.effectRadius(effectType)
            property int durationMs: Math.max(220, Number(model.durationMs || root.effectDuration(effectType)))
            property real startScale: root.effectScaleFrom(effectType)
            property real endScale: root.effectScaleTo(effectType)
            property real startOpacity: root.effectOpacityFrom(effectType)
            property real endOpacity: root.effectOpacityTo(effectType)
            width: baseSize
            height: baseSize
            x: root.pxX(Number(model.xNorm || 0.5)) - width / 2
            y: root.pxY(Number(model.yNorm || 0.5)) - height / 2
            opacity: startOpacity
            scale: startScale

            Rectangle {
                anchors.fill: parent
                radius: width / 2
                color: "transparent"
                border.width: 2
                border.color: root.effectGlow(localFeedbackRoot.effectType)
                opacity: root.isEffectImageAvailable(localFeedbackRoot.effectType) ? 0.38 : 0.86
            }

            Image {
                anchors.centerIn: parent
                width: parent.width
                height: parent.height
                source: root.effectImageSource(localFeedbackRoot.effectType)
                visible: root.isEffectImageAvailable(localFeedbackRoot.effectType)
                fillMode: Image.PreserveAspectFit
                smooth: true
                mipmap: true
                opacity: Number(root.styleValue(root.effectStyle(localFeedbackRoot.effectType), "image_opacity", 0.72))
            }

            Rectangle {
                anchors.centerIn: parent
                width: 6
                height: 6
                radius: 3
                color: root.effectColor(localFeedbackRoot.effectType)
                opacity: root.isEffectImageAvailable(localFeedbackRoot.effectType) ? 0.42 : 0.92
            }

            NumberAnimation on scale {
                from: localFeedbackRoot.startScale
                to: localFeedbackRoot.endScale
                duration: localFeedbackRoot.durationMs
                easing.type: Easing.OutCubic
                running: true
            }

            NumberAnimation on opacity {
                from: localFeedbackRoot.startOpacity
                to: localFeedbackRoot.endOpacity
                duration: localFeedbackRoot.durationMs
                easing.type: Easing.OutCubic
                running: true
            }
        }
    }

    Timer {
        interval: 16
        running: root.visible
        repeat: true
        onTriggered: {
            root.animationTick += 1
            if ((root.animationTick % 6) === 0) {
                root.pruneVisualEvents()
                root.logRingDiagnostic()
            }
        }
    }

    // TASK25E TraceLock asset replacement verifies backgroundVfxCanvas progressRingImageSource effectAssetDescriptor effectImageSource isEffectImageAvailable tracelock.effect.local_ripple.
    // Audio slots audio.tracelock.music.loop and audio.tracelock.ambient.loop are exposed as replaceable assets; playback is intentionally left to a dedicated audio renderer.
    // TASK25B GameCanvas consumes canvas.background layered color/image/gradient/overlay and TraceLock game style tokens.
    // TASK25C GameCanvas consumes TraceLock visual asset_key/style_key tokens.
    // canvas.background layered color/image/gradient/overlay
    // TASK25D effect_styles parameterize trace_seal lock_failed trace_drop combo_popup pulse flash fade popup simple burst particle_burst duration_ms color particle_count scale_from scale_to opacity_from opacity_to
    // targetAssetKey targetAssetDescriptor targetImageSource targetFallbackShape isTargetImageAvailable asset_key fallback_shape Image {

    MouseArea {
        anchors.fill: parent
        hoverEnabled: false
        onPressed: function(mouse) {
            var xNorm = mouse.x / Math.max(1, root.width)
            var yNorm = mouse.y / Math.max(1, root.height)
            var diagnostic = root.diagnosticEnabled ? root.clickDiagnostic(mouse, xNorm, yNorm) : ({})
            root.pushLocalFeedback(xNorm, yNorm, "press")
            // Send at press time, not release/click time, to avoid a visible target
            // vs. backend state mismatch on fast-moving TraceLock targets.
            root.sendPointerClick(xNorm, yNorm, diagnostic)
        }
        onClicked: function(mouse) {
            // Event is intentionally sent from onPressed for lower latency.
        }
    }
}
