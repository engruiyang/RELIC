import QtQuick
import QtQuick.Controls

Column {
    id: root

    property string titleText: ""
    property string subtitleText: ""
    property var designThemeObj: ({})
    property var componentStyleObj: ({})
    property var headerStyleObj: ({})
    property var renderResourcesObj: ({})

    spacing: 2

    readonly property color textColor: (designThemeObj.colors && designThemeObj.colors.text) ? designThemeObj.colors.text : "#0F172A"
    readonly property color mutedTextColor: (designThemeObj.colors && designThemeObj.colors.text_muted) ? designThemeObj.colors.text_muted : "#475569"
    readonly property var effectiveStyleObj: Object.keys(headerStyleObj || ({})).length > 0 ? headerStyleObj : ((componentStyleObj || ({})).header || ({}))

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

    Label {
        text: root.titleText
        font.pixelSize: Number(root.styleValue(root.effectiveStyleObj, "title_size", (root.designThemeObj.typography || ({})).title_size || 20))
        font.bold: true
        color: root.styleValue(root.effectiveStyleObj, "title_color", root.textColor)
    }

    Label {
        text: root.subtitleText
        color: root.styleValue(root.effectiveStyleObj, "subtitle_color", root.mutedTextColor)
        wrapMode: Text.WordWrap
    }

    Image {
        width: parent.width > 0 ? parent.width : 420
        height: Number(root.styleValue(root.effectiveStyleObj, "decorator_height", 3))
        source: root.assetSource(root.styleValue(root.effectiveStyleObj, "decorator_asset_key", ""))
        visible: source !== ""
        fillMode: Image.Stretch
        smooth: true
        cache: false
    }

    Rectangle {
        width: parent.width > 0 ? parent.width : 420
        height: Number(root.styleValue(root.effectiveStyleObj, "decorator_height", 3))
        color: root.styleValue(root.effectiveStyleObj, "accent", "#2563EB")
        opacity: sourceFallbackVisible ? 0.65 : 0.0
        property bool sourceFallbackVisible: root.styleValue(root.effectiveStyleObj, "decorator_asset_key", "") !== "" && root.assetSource(root.styleValue(root.effectiveStyleObj, "decorator_asset_key", "")) === ""
    }

    // TASK25E-1 PageHeader consumes decorator_asset_key through renderResourcesObj.
}
