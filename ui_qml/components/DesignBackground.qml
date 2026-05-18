import QtQuick

Item {
    id: root

    property var styleObj: ({})
    property var themeObj: ({})
    property var renderResourcesObj: ({})
    property color fallbackColor: "#0f1720"

    function value(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function colors() {
        return themeObj.colors || ({})
    }

    function resolveThemePath(path, fallbackValue) {
        if (path === undefined || path === null || path === "") {
            return fallbackValue
        }
        var text = String(path)
        if (text.indexOf("theme.colors.") === 0) {
            return value(colors(), text.substring("theme.colors.".length), fallbackValue)
        }
        return text
    }

    function backgroundSpec() {
        var bg = styleObj.background
        if (bg === undefined || bg === null || bg === "") {
            bg = value(colors(), "background", fallbackColor)
        }
        if (typeof bg === "string") {
            return ({"type": "color", "value": resolveThemePath(bg, fallbackColor)})
        }
        return bg
    }

    function layers() {
        var bg = backgroundSpec()
        if (bg.layers && Array.isArray(bg.layers)) {
            return bg.layers
        }
        return [bg]
    }

    function layerAt(index) {
        var arr = layers()
        if (index >= 0 && index < arr.length) {
            return arr[index] || ({})
        }
        return ({})
    }

    function firstLayer(typeName) {
        var arr = layers()
        for (var i = 0; i < arr.length; i++) {
            if (String(arr[i].type || "") === typeName) {
                return arr[i]
            }
        }
        return ({})
    }

    function colorValue(fallbackValue) {
        var colorLayer = firstLayer("color")
        if (colorLayer.value !== undefined) {
            return resolveThemePath(colorLayer.value, fallbackValue)
        }
        var bg = backgroundSpec()
        if (bg.type === "color") {
            return resolveThemePath(bg.value, fallbackValue)
        }
        return fallbackValue
    }

    function gradientLayer() {
        return firstLayer("gradient")
    }

    function overlayLayer() {
        return firstLayer("overlay")
    }

    function imageLayer() {
        return firstLayer("image")
    }

    function assetUrl(assetKey) {
        if (assetKey === undefined || assetKey === null || assetKey === "") {
            return ""
        }
        var assets = renderResourcesObj.assets || ({})
        var item = assets[String(assetKey)] || ({})
        return item.url || ""
    }

    function imageSource() {
        var layer = imageLayer()
        if (layer.url !== undefined && layer.url !== null && layer.url !== "") {
            return String(layer.url)
        }
        return assetUrl(layer.asset_key)
    }

    function imageOpacity() {
        var layer = imageLayer()
        return Number(value(layer, "opacity", 0.0))
    }

    function imageFillMode() {
        var fit = String(value(imageLayer(), "fit", "cover"))
        if (fit === "contain") {
            return Image.PreserveAspectFit
        }
        if (fit === "stretch") {
            return Image.Stretch
        }
        if (fit === "tile") {
            return Image.Tile
        }
        return Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: root.colorValue(root.fallbackColor)
    }

    Image {
        anchors.fill: parent
        source: root.imageSource()
        visible: source !== ""
        fillMode: root.imageFillMode()
        opacity: root.imageOpacity()
        smooth: true
        clip: true
    }

    Rectangle {
        anchors.fill: parent
        visible: root.gradientLayer().from !== undefined || root.gradientLayer().to !== undefined
        opacity: Number(root.value(root.gradientLayer(), "opacity", 0.45))
        gradient: Gradient {
            GradientStop { position: 0.0; color: root.value(root.gradientLayer(), "from", "#00000000") }
            GradientStop { position: 1.0; color: root.value(root.gradientLayer(), "to", "#00000000") }
        }
    }

    Rectangle {
        anchors.fill: parent
        visible: root.overlayLayer().value !== undefined
        color: root.value(root.overlayLayer(), "value", "#000000")
        opacity: Number(root.value(root.overlayLayer(), "opacity", 0.0))
    }

    // TASK25B background supports color / image asset_key / gradient / overlay / opacity / fit / position fallback.
}
