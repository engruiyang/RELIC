import QtQuick

Rectangle {
    id: root

    property var themeObj: ({})
    property var panelStyleObj: ({})
    property var renderResourcesObj: ({})

    function styleValue(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
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

    function assetSource(assetKey) {
        var desc = root.assetDescriptor(assetKey)
        return root.normalizedAssetUrl(desc.url || "")
    }

    color: root.styleValue(root.panelStyleObj, "background", (root.themeObj.colors ? root.themeObj.colors.panel : "#FFFFFF"))
    border.color: root.styleValue(root.panelStyleObj, "border", (root.themeObj.colors ? root.themeObj.colors.panel_border : "#CBD5E1"))
    border.width: Number(root.styleValue(root.panelStyleObj, "border_width", 1))
    radius: Number(root.styleValue(root.panelStyleObj, "radius", 10))
    opacity: Number(root.styleValue(root.panelStyleObj, "opacity", 0.96))
    clip: true

    Image {
        anchors.fill: parent
        source: root.assetSource(root.styleValue(root.panelStyleObj, "background_asset_key", ""))
        visible: source !== ""
        fillMode: Image.Stretch
        smooth: true
        cache: false
    }

    Image {
        anchors.fill: parent
        source: root.assetSource(root.styleValue(root.panelStyleObj, "frame_asset_key", ""))
        visible: source !== ""
        fillMode: Image.Stretch
        smooth: true
        cache: false
    }

    // TASK25E-1 DesignPanel consumes background_asset_key / frame_asset_key through renderResourcesObj.
}
