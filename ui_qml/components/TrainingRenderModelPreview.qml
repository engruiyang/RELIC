import QtQuick 2.15

Item {
    id: root

    property string pageId: "training"
    property int cardCount: 0
    property int widgetCount: 0
    property string requiredCardsText: "n/a"
    property string actionsText: "n/a"
    property string sourceRootsText: "n/a"
    property string placeholderSourcesText: "n/a"
    property string gameCanvasStatusText: "n/a"
    property bool safeStopPresent: false
    property string slotsSupportedText: "false"
    property string injectionSupportedText: "false"

    implicitWidth: 760
    implicitHeight: 420

    DesignCard {
        anchors.fill: parent
        cardTitle: "Training Render Model Preview"
        cardSubtitle: "TASK26F-1 bridge summary preview"
        backgroundColor: "#111827"
        borderColor: root.safeStopPresent ? "#22C55E" : "#EF4444"

        Column {
            anchors.fill: parent
            spacing: 8

            Row {
                width: parent.width
                spacing: 12

                ConfigTextWidget {
                    width: (parent.width - 24) / 3
                    label: "Page"
                    value: root.pageId
                }

                ConfigTextWidget {
                    width: (parent.width - 24) / 3
                    label: "Cards"
                    value: String(root.cardCount)
                }

                ConfigTextWidget {
                    width: (parent.width - 24) / 3
                    label: "Widgets"
                    value: String(root.widgetCount)
                }
            }

            ConfigTextWidget {
                width: parent.width
                label: "Required Cards"
                value: root.requiredCardsText
            }

            ConfigTextWidget {
                width: parent.width
                label: "Actions"
                value: root.actionsText
            }

            ConfigTextWidget {
                width: parent.width
                label: "Source Roots"
                value: root.sourceRootsText
            }

            ConfigTextWidget {
                width: parent.width
                label: "Placeholder Sources"
                value: root.placeholderSourcesText
            }

            ConfigTextWidget {
                width: parent.width
                label: "GameCanvas"
                value: root.gameCanvasStatusText
            }

            Row {
                width: parent.width
                spacing: 12

                ConfigTextWidget {
                    width: (parent.width - 24) / 3
                    label: "Safe Stop"
                    value: root.safeStopPresent ? "present" : "missing"
                }

                ConfigTextWidget {
                    width: (parent.width - 24) / 3
                    label: "Slots"
                    value: root.slotsSupportedText
                }

                ConfigTextWidget {
                    width: (parent.width - 24) / 3
                    label: "Injection"
                    value: root.injectionSupportedText
                }
            }
        }
    }
}
