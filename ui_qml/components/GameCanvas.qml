import QtQuick

Rectangle {
    id: root
    property var gameView: ({})
    property var entities: (gameView && gameView.entities) ? gameView.entities : []
    property var guiBridgeRef: null
    property string fallbackGameId: "fake_game"

    color: "#1a1a1a"
    border.width: 1
    border.color: "#888"

    function pxX(xNorm) { return Math.max(0, Math.min(width, xNorm * width)) }
    function pxY(yNorm) { return Math.max(0, Math.min(height, yNorm * height)) }
    function pxRadius(rNorm) { return Math.max(4, rNorm * Math.min(width, height)) }

    Text {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 8
        color: "#ddd"
        text: "GameCanvas | entities=" + root.entities.length
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
                anchors.fill: parent
                radius: width / 2
                color: entity.kind === "target" ? "#f44" : (entity.kind === "focus_zone" ? "#44aaff44" : "transparent")
                border.width: entity.kind === "progress_ring" ? 3 : (entity.state === "active" ? 2 : 1)
                border.color: entity.kind === "progress_ring" ? "#ffdd55" : "#dddddd"
                visible: entity.kind === "target" || entity.kind === "focus_zone" || entity.kind === "progress_ring"
            }
            Text {
                anchors.centerIn: parent
                color: "#ddd"
                text: entity.kind === "progress_ring" ? ("P " + Math.round((entity.metadata && entity.metadata.progress ? entity.metadata.progress : 0) * 100) + "%") : ""
                visible: entity.kind === "progress_ring"
                font.pixelSize: 11
            }
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
