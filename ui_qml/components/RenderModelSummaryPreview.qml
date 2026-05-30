import QtQuick 2.15

Item {
    id: root

    property string previewTitle: "Render Model Preview"
    property string previewSubtitle: ""
    property string pageId: ""
    property int cardCount: 0
    property int widgetCount: 0

    property bool showRequiredLockedCounts: false
    property int requiredCardCount: 0
    property int lockedCardCount: 0
    property string cardIdsText: "n/a"

    property string requiredCardsText: "n/a"
    property string actionsText: "n/a"
    property string sourceRootsText: "n/a"
    property string placeholderSourcesText: "n/a"
    property string gameCanvasStatusText: "n/a"
    property bool safeStopPresent: false
    property string slotsSupportedText: "false"
    property string injectionSupportedText: "false"

    property bool showCardIds: false
    property bool showRequiredCardsText: false
    property bool showPlaceholderSources: false
    property bool showGameCanvasStatus: false
    property bool showSafeStopAndSupport: false

    property color backgroundColor: "#111A25"
    property color borderColor: "#3B5674"
    property color safeBorderColor: "#22C55E"
    property color dangerBorderColor: "#EF4444"
    property bool useSafeStopBorder: false

    implicitWidth: 760
    implicitHeight: showSafeStopAndSupport ? 420 : 360

    DesignCard {
        anchors.fill: parent
        cardTitle: root.previewTitle
        cardSubtitle: root.previewSubtitle
        backgroundColor: root.backgroundColor
        borderColor: root.useSafeStopBorder ? (root.safeStopPresent ? root.safeBorderColor : root.dangerBorderColor) : root.borderColor

        Column {
            anchors.fill: parent
            spacing: 6

            Row {
                width: parent.width
                spacing: 12
                visible: root.showSafeStopAndSupport

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
                visible: !root.showSafeStopAndSupport
                label: "Page"
                value: root.pageId
            }

            ConfigTextWidget {
                width: parent.width
                visible: !root.showSafeStopAndSupport
                label: "Cards"
                value: String(root.cardCount)
            }

            ConfigTextWidget {
                width: parent.width
                visible: !root.showSafeStopAndSupport
                label: "Widgets"
                value: String(root.widgetCount)
            }

            ConfigTextWidget {
                width: parent.width
                visible: root.showRequiredLockedCounts
                label: "Required Cards"
                value: String(root.requiredCardCount)
            }

            ConfigTextWidget {
                width: parent.width
                visible: root.showRequiredLockedCounts
                label: "Locked Cards"
                value: String(root.lockedCardCount)
            }

            ConfigTextWidget {
                width: parent.width
                visible: root.showRequiredCardsText
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
                visible: root.showCardIds
                label: "Card IDs"
                value: root.cardIdsText
            }

            ConfigTextWidget {
                width: parent.width
                visible: root.showPlaceholderSources
                label: "Placeholder Sources"
                value: root.placeholderSourcesText
            }

            ConfigTextWidget {
                width: parent.width
                visible: root.showGameCanvasStatus
                label: "GameCanvas"
                value: root.gameCanvasStatusText
            }

            Row {
                width: parent.width
                spacing: 12
                visible: root.showSafeStopAndSupport

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
