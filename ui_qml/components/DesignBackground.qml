import QtQuick

Item {
    id: root

    property var styleObj: ({})
    property var themeObj: ({})
    property var renderResourcesObj: ({})
    property color fallbackColor: "#F8FAFC"

    function value(obj, key, fallbackValue) {
        if (obj === undefined || obj === null) {
            return fallbackValue
        }
        var v = obj[key]
        return (v === undefined || v === null || v === "") ? fallbackValue : v
    }

    function colors() {
        return root.themeObj.colors || ({})
    }

    function resolveThemePath(path, fallbackValue) {
        if (path === undefined || path === null || path === "") {
            return fallbackValue
        }
        var text = String(path)
        if (text.indexOf("theme.colors.") === 0) {
            return root.value(root.colors(), text.substring("theme.colors.".length), fallbackValue)
        }
        return text
    }

    function backgroundSpec() {
        var bg = root.styleObj.background
        if ((bg === undefined || bg === null || bg === "") && root.styleObj.layered !== undefined) {
            bg = root.styleObj.layered
        }
        if (bg === undefined || bg === null || bg === "") {
            bg = root.value(root.colors(), "background", root.fallbackColor)
        }
        if (typeof bg === "string") {
            return ({"type": "color", "value": root.resolveThemePath(bg, root.fallbackColor)})
        }
        if (bg.layers && Array.isArray(bg.layers)) {
            return bg
        }
        if (bg.color !== undefined || bg.image !== undefined || bg.gradient !== undefined || bg.overlay !== undefined || bg.asset_key !== undefined) {
            var layers = []
            if (bg.color !== undefined) {
                layers.push({"type": "color", "value": bg.color, "opacity": root.value(bg, "opacity", 1.0)})
            }
            if (bg.image !== undefined || bg.asset_key !== undefined) {
                var image = bg.image || ({})
                if (typeof bg.image === "object") {
                    layers.push({
                        "type": "image",
                        "asset_key": root.value(image, "asset_key", root.value(bg, "asset_key", "")),
                        "url": root.value(image, "url", ""),
                        "opacity": root.value(image, "opacity", root.value(bg, "image_opacity", 1.0)),
                        "fit": root.value(image, "fit", root.value(bg, "fit", "cover")),
                        "position": root.value(image, "position", "center")
                    })
                } else {
                    layers.push({
                        "type": "image",
                        "asset_key": root.value(bg, "asset_key", String(image)),
                        "opacity": root.value(bg, "image_opacity", 1.0),
                        "fit": root.value(bg, "fit", "cover"),
                        "position": root.value(bg, "position", "center")
                    })
                }
            }
            if (bg.gradient !== undefined) {
                var gradient = bg.gradient || ({})
                if (root.value(gradient, "enabled", true) !== false) {
                    layers.push({
                        "type": "gradient",
                        "from": root.value(gradient, "from", "#00000000"),
                        "to": root.value(gradient, "to", "#00000000"),
                        "opacity": root.value(gradient, "opacity", root.value(bg, "gradient_opacity", 0.45)),
                        "angle": root.value(gradient, "angle", 180),
                        "direction": root.value(gradient, "direction", "vertical")
                    })
                }
            }
            if (bg.overlay !== undefined) {
                var overlay = bg.overlay || ({})
                layers.push({
                    "type": "overlay",
                    "value": root.value(overlay, "color", overlay),
                    "opacity": root.value(overlay, "opacity", 0.0)
                })
            }
            return ({"type": "layered", "layers": layers})
        }
        return bg
    }

    function layers() {
        var bg = root.backgroundSpec()
        if (bg.layers && Array.isArray(bg.layers)) {
            return bg.layers
        }
        return [bg]
    }

    function firstLayer(typeName) {
        var arr = root.layers()
        for (var i = 0; i < arr.length; i++) {
            if (String(arr[i].type || "") === typeName) {
                return arr[i]
            }
        }
        return ({})
    }

    function colorValue(fallbackValue) {
        var colorLayer = root.firstLayer("color")
        if (colorLayer.value !== undefined) {
            return root.resolveThemePath(colorLayer.value, fallbackValue)
        }
        var bg = root.backgroundSpec()
        if (bg.type === "color") {
            return root.resolveThemePath(bg.value, fallbackValue)
        }
        return fallbackValue
    }

    function gradientLayer() {
        return root.firstLayer("gradient")
    }

    function overlayLayer() {
        return root.firstLayer("overlay")
    }

    function imageLayer() {
        return root.firstLayer("image")
    }

    function normalizedUrl(rawUrl) {
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

    function assetUrl(assetKey) {
        if (assetKey === undefined || assetKey === null || assetKey === "") {
            return ""
        }
        var assets = root.renderResourcesObj.assets || ({})
        var item = assets[String(assetKey)] || ({})
        return root.normalizedUrl(item.url || "")
    }

    function imageSource() {
        var layer = root.imageLayer()
        if (layer.url !== undefined && layer.url !== null && layer.url !== "") {
            return root.normalizedUrl(layer.url)
        }
        return root.assetUrl(layer.asset_key)
    }

    function imageOpacity() {
        var layer = root.imageLayer()
        return Number(root.value(layer, "opacity", 1.0))
    }

    function imageFillMode() {
        var fit = String(root.value(root.imageLayer(), "fit", "cover"))
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
        asynchronous: true
        cache: false
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
