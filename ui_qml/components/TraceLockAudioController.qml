import QtQuick
import QtMultimedia

Item {
    id: root

    // TraceLockAudioController is deliberately independent from GameCanvas.
    // It resolves replaceable audio URLs from renderResourcesObj and performs
    // real QtMultimedia playback only when playback_enabled is explicitly true.
    objectName: "traceLockAudioController"

    property var renderResourcesObj: ({})
    property var gameHudObj: ({})
    property var gameViewObj: ({})
    property bool playbackEnabled: false
    property bool musicEnabled: false
    property bool ambientEnabled: false
    property bool sfxEnabled: false
    property bool diagnosticEnabled: false

    property real musicVolume: 0.28
    property real ambientVolume: 0.18
    property real sfxVolume: 0.55

    property string musicKey: "audio.tracelock.music.loop"
    property string ambientKey: "audio.tracelock.ambient.loop"
    property string hitKey: "audio.tracelock.hit"
    property string missKey: "audio.tracelock.miss"
    property string comboKey: "audio.tracelock.combo"
    property string uiClickKey: "audio.ui.click"

    property string musicSource: audioSource(musicKey)
    property string ambientSource: audioSource(ambientKey)
    property string hitSource: audioSource(hitKey)
    property string missSource: audioSource(missKey)
    property string comboSource: audioSource(comboKey)
    property string uiClickSource: audioSource(uiClickKey)

    property bool gameRunning: boolValue(gameHudObj.game_running, false)
    property var consumedVisualEventIds: ({})

    function boolValue(v, fallbackValue) {
        if (v === true || v === "true" || v === 1 || v === "1") return true
        if (v === false || v === "false" || v === 0 || v === "0") return false
        return fallbackValue
    }

    function styleValue(styleObj, key, fallbackValue) {
        if (!styleObj) return fallbackValue
        var v = styleObj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function audioDescriptor(audioKey) {
        var assets = renderResourcesObj.assets || ({})
        return assets[audioKey] || ({})
    }

    function audioStyle(audioKey) {
        var styles = renderResourcesObj.styles || ({})
        return styles[audioKey] || ({})
    }

    function audioSource(audioKey) {
        var desc = audioDescriptor(audioKey)
        var url = String(desc.resolved_url || desc.url || "")
        return url
    }

    function hasAudioSource(audioKey) {
        return audioSource(audioKey).length > 0
    }

    function effectiveVolume(audioKey, fallbackVolume) {
        var s = audioStyle(audioKey)
        var v = Number(styleValue(s, "volume", fallbackVolume))
        if (isNaN(v)) return fallbackVolume
        return Math.max(0.0, Math.min(1.0, v))
    }

    function playableUrl(rawSource) {
        var u = String(rawSource || "")
        if (u.length === 0) return ""
        if (u.indexOf("file:") === 0 || u.indexOf("qrc:") === 0 || u.indexOf("http:") === 0 || u.indexOf("https:") === 0) return u

        // Windows absolute path, for example F:\relic\...
        if (u.length > 2 && u.charAt(1) === ":") {
            return "file:///" + u.replace(/\\/g, "/")
        }

        // Manifest URLs are repository-relative without the leading assets/.
        if (u.indexOf("assets/") === 0) {
            return Qt.resolvedUrl("../../" + u)
        }
        if (u.indexOf("packs/") === 0) {
            return Qt.resolvedUrl("../../assets/" + u)
        }
        return Qt.resolvedUrl("../../assets/" + u)
    }

    function shouldPlayMusic() {
        return playbackEnabled && musicEnabled && gameRunning && hasAudioSource(musicKey)
    }

    function shouldPlayAmbient() {
        return playbackEnabled && ambientEnabled && gameRunning && hasAudioSource(ambientKey)
    }

    function updateMusicState(reason) {
        if (shouldPlayMusic()) {
            if (musicPlayer.source !== playableUrl(musicSource)) {
                musicPlayer.source = playableUrl(musicSource)
            }
            musicOutput.volume = effectiveVolume(musicKey, musicVolume)
            if (musicPlayer.playbackState !== MediaPlayer.PlayingState) {
                musicPlayer.play()
            }
            if (diagnosticEnabled) console.log("[TRACELOCK AUDIO MUSIC] play " + String(reason || "n/a"))
        } else {
            if (musicPlayer.playbackState !== MediaPlayer.StoppedState) {
                musicPlayer.stop()
            }
            if (diagnosticEnabled) console.log("[TRACELOCK AUDIO MUSIC] stop " + String(reason || "n/a"))
        }

        if (shouldPlayAmbient()) {
            if (ambientPlayer.source !== playableUrl(ambientSource)) {
                ambientPlayer.source = playableUrl(ambientSource)
            }
            ambientOutput.volume = effectiveVolume(ambientKey, ambientVolume)
            if (ambientPlayer.playbackState !== MediaPlayer.PlayingState) {
                ambientPlayer.play()
            }
            if (diagnosticEnabled) console.log("[TRACELOCK AUDIO AMBIENT] play " + String(reason || "n/a"))
        } else {
            if (ambientPlayer.playbackState !== MediaPlayer.StoppedState) {
                ambientPlayer.stop()
            }
        }
    }

    function soundEffectForKey(audioKey) {
        if (audioKey === hitKey) return hitSound
        if (audioKey === missKey) return missSound
        if (audioKey === comboKey) return comboSound
        if (audioKey === uiClickKey) return uiClickSound
        return null
    }

    function playSfx(audioKey, reason) {
        if (!playbackEnabled || !sfxEnabled) return
        if (!hasAudioSource(audioKey)) return
        var sound = soundEffectForKey(audioKey)
        if (!sound) return

        sound.volume = effectiveVolume(audioKey, sfxVolume)
        sound.play()
        if (diagnosticEnabled) {
            console.log("[TRACELOCK AUDIO SFX] " + JSON.stringify({"audio_key": audioKey, "reason": reason || "n/a", "source": audioSource(audioKey)}))
        }
    }

    function visualEventAudioKey(evt) {
        var kind = String((evt && (evt.kind || evt.type || evt.effect_type)) || "")
        var effectKey = String((evt && (evt.effect_key || evt.style_key)) || "")
        var text = kind + " " + effectKey

        if (text.indexOf("combo_popup") >= 0 || text.indexOf("combo") >= 0) return comboKey
        if (text.indexOf("trace_seal") >= 0 || text.indexOf("target_click") >= 0) return hitKey
        if (text.indexOf("lock_failed") >= 0 || text.indexOf("trace_drop") >= 0 || text.indexOf("miss") >= 0) return missKey
        return ""
    }

    function visualEventSignature(evt, index) {
        if (!evt) return "empty:" + String(index)
        var explicitId = evt.event_id || evt.id || ""
        if (explicitId) return String(explicitId)
        return String(gameViewObj.frame_id || "frame") + ":" + String(evt.kind || evt.type || evt.effect_key || "event") + ":" + String(evt.target_id || index)
    }

    function consumeVisualEvents(reason) {
        if (!playbackEnabled || !sfxEnabled) return
        var events = gameViewObj.visual_events || gameViewObj.visualEvents || []
        for (var i = 0; i < events.length; i++) {
            var evt = events[i]
            var sig = visualEventSignature(evt, i)
            if (consumedVisualEventIds[sig]) continue

            consumedVisualEventIds[sig] = true
            var key = visualEventAudioKey(evt)
            if (key.length > 0) {
                playSfx(key, reason || "visual_event")
            }
        }
    }

    MediaPlayer {
        id: musicPlayer
        audioOutput: AudioOutput { id: musicOutput; volume: 0.0 }
        onMediaStatusChanged: {
            if (mediaStatus === MediaPlayer.EndOfMedia && root.shouldPlayMusic()) {
                stop()
                play()
            }
        }
    }

    MediaPlayer {
        id: ambientPlayer
        audioOutput: AudioOutput { id: ambientOutput; volume: 0.0 }
        onMediaStatusChanged: {
            if (mediaStatus === MediaPlayer.EndOfMedia && root.shouldPlayAmbient()) {
                stop()
                play()
            }
        }
    }

    SoundEffect {
        id: hitSound
        source: root.playableUrl(root.hitSource)
        volume: root.effectiveVolume(root.hitKey, root.sfxVolume)
    }

    SoundEffect {
        id: missSound
        source: root.playableUrl(root.missSource)
        volume: root.effectiveVolume(root.missKey, root.sfxVolume)
    }

    SoundEffect {
        id: comboSound
        source: root.playableUrl(root.comboSource)
        volume: root.effectiveVolume(root.comboKey, root.sfxVolume)
    }

    SoundEffect {
        id: uiClickSound
        source: root.playableUrl(root.uiClickSource)
        volume: root.effectiveVolume(root.uiClickKey, root.sfxVolume)
    }

    onGameRunningChanged: updateMusicState("gameRunningChanged")
    onMusicSourceChanged: updateMusicState("musicSourceChanged")
    onAmbientSourceChanged: updateMusicState("ambientSourceChanged")
    onPlaybackEnabledChanged: updateMusicState("playbackEnabledChanged")
    onMusicEnabledChanged: updateMusicState("musicEnabledChanged")
    onAmbientEnabledChanged: updateMusicState("ambientEnabledChanged")
    onGameHudObjChanged: updateMusicState("gameHudObjChanged")
    onGameViewObjChanged: consumeVisualEvents("gameViewObjChanged")

    // Contract tokens:
    // QtMultimedia MediaPlayer AudioOutput SoundEffect
    // audio.tracelock.music.loop audio.tracelock.ambient.loop audio.tracelock.hit audio.tracelock.miss audio.tracelock.combo audio.ui.click
}
