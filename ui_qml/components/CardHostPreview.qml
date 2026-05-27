import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var guiBridge: null

    implicitWidth: 760
    implicitHeight: 420

    GridLayout {
        anchors.fill: parent
        anchors.margins: 12
        columns: 2
        rowSpacing: 12
        columnSpacing: 12

        DesignCard {
            id: runtimeCard
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: 180
            cardTitle: "Runtime I/O"
            cardSubtitle: "Connection, stream, attention and gyro freshness"
            backgroundColor: "#111923"
            borderColor: "#2F7D9E"

            ConfigMetricWidget {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.right: parent.right
                label: "Connection"
                value: "preview-connected"
                level: "ok"
            }

            ConfigMetricWidget {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.topMargin: 68
                anchors.right: parent.right
                label: "Attention Age"
                value: "820"
                unit: "ms"
                freshnessAgeMs: 820
            }
        }

        DesignCard {
            id: actionCard
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: 180
            cardTitle: "Quick Actions"
            cardSubtitle: "Button widgets only emit registered action ids"
            backgroundColor: "#151A24"
            borderColor: "#7B5D2D"

            ConfigButtonWidget {
                id: refreshButton
                anchors.left: parent.left
                anchors.top: parent.top
                label: "Refresh"
                actionId: "app.refresh_now"
                variant: "primary"
                guiBridge: root.guiBridge
            }

            ConfigButtonWidget {
                id: safeStopButton
                anchors.left: parent.left
                anchors.top: refreshButton.bottom
                anchors.topMargin: 12
                label: "Safe Stop"
                actionId: "live.safe_stop"
                variant: "danger"
                required: true
                confirmEnabled: true
                confirmMessage: "Click again"
                guiBridge: root.guiBridge
            }
        }

        DesignCard {
            id: sessionCard
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: 180
            cardTitle: "Session"
            cardSubtitle: "Preview of session card fields"
            backgroundColor: "#121820"
            borderColor: "#3A4A64"

            ConfigTextWidget {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.right: parent.right
                label: "Session Active"
                value: "false"
            }

            ConfigTextWidget {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.topMargin: 52
                anchors.right: parent.right
                label: "Current Session"
                value: "n/a"
            }
        }

        DesignCard {
            id: identityCard
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: 180
            cardTitle: "RELIC Desktop Card System"
            cardSubtitle: "TASK26B isolated preview"
            backgroundColor: "#10151F"
            borderColor: "#5B6C86"

            ConfigTextWidget {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.right: parent.right
                label: "Mode"
                value: "preview-only"
            }

            ConfigTextWidget {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.topMargin: 52
                anchors.right: parent.right
                label: "Legacy GUI"
                value: "kept as fallback"
            }
        }
    }
}
