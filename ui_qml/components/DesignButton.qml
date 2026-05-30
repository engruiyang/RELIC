import QtQuick

Item {
    id: root

    property string text: ""
    property var buttonStyleObj: ({})
    property var themeObj: ({})
    property var renderResourcesObj: ({})
    signal clicked()
    signal pressed()
    signal released()

    implicitWidth: Math.max(128, label.implicitWidth + 28)
    implicitHeight: Math.max(34, label.implicitHeight + 16)
    width: implicitWidth
    height: implicitHeight
    clip: true

    readonly property bool down: mouseArea.pressed
    readonly property bool hovered: mouseArea.containsMouse
    readonly property var colorsObj: themeObj.colors || ({})
    readonly property var normalObj: buttonStyleObj.normal || ({})
    readonly property var pressedObj: buttonStyleObj.pressed || ({})
    readonly property var disabledObj: buttonStyleObj.disabled || ({})

    function styleValue(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function stateStyle() {
        if (!root.enabled) {
            return root.disabledObj
        }
        if (root.down) {
            return root.pressedObj
        }
        return root.normalObj
    }

    function assetDescriptor(assetKey) {
        if (assetKey === undefined || assetKey === null || assetKey === "") {
            return ({})
        }
        var assets = root.renderResourcesObj.assets || ({})
        return assets[String(assetKey)] || ({})
    }

    function normalizedAssetUrl(rawUrl) {
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

    function buttonAssetKey() {
        return root.styleValue(root.stateStyle(), "asset_key", "")
    }

    function buttonImageSource() {
        var key = root.buttonAssetKey()
        if (key === "") {
            return ""
        }
        var desc = root.assetDescriptor(key)
        return root.normalizedAssetUrl(desc.url || root.styleValue(root.stateStyle(), "url", ""))
    }

    Rectangle {
        anchors.fill: parent
        radius: Number(root.styleValue(root.buttonStyleObj, "radius", 8))
        color: !root.enabled
               ? root.styleValue(root.disabledObj, "background", "#CBD5E1")
               : (root.down
                  ? root.styleValue(root.pressedObj, "background", "#1D4ED8")
                  : root.styleValue(root.normalObj, "background", root.styleValue(root.colorsObj, "accent", "#2563EB")))
        border.width: 1
        border.color: !root.enabled
                      ? root.styleValue(root.disabledObj, "border", "#94A3B8")
                      : (root.down
                         ? root.styleValue(root.pressedObj, "border", "#1E40AF")
                         : root.styleValue(root.normalObj, "border", "#1D4ED8"))
        opacity: root.enabled ? 1.0 : 0.65
    }

    Image {
        anchors.fill: parent
        source: root.buttonImageSource()
        visible: source !== ""
        fillMode: Image.Stretch
        smooth: true
        cache: false
        opacity: root.enabled ? 1.0 : 0.55
    }

    Text {
        id: label
        anchors.centerIn: parent
        width: parent.width - 16
        text: root.text
        color: !root.enabled
               ? root.styleValue(root.disabledObj, "text", "#64748B")
               : (root.down
                  ? root.styleValue(root.pressedObj, "text", "#FFFFFF")
                  : root.styleValue(root.normalObj, "text", "#FFFFFF"))
        font.pixelSize: Number(((root.themeObj.typography || ({})).body_size) || 14)
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        enabled: root.enabled
        onPressed: root.pressed()
        onReleased: root.released()
        onClicked: root.clicked()
    }

    // TASK25E-1 DesignButton consumes normal/pressed/disabled asset_key through renderResourcesObj.
}
