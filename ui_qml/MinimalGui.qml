import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 1000
    height: 700
    title: "RELIC Core"

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 10

        Label {
            text: "RELIC Core / TraceLock Control Shell"
            font.pixelSize: 24
            font.bold: true
        }

        Label {
            text: "QML smoke shell loaded"
            font.pixelSize: 16
        }

        GroupBox {
            width: parent.width
            title: "Protocol Select"
            Label { text: "Protocol Select" }
        }

        GroupBox {
            width: parent.width
            title: "TraceLock Training"
            Label { text: "TraceLock Training" }
        }

        GroupBox {
            width: parent.width
            title: "Training Controls"
            Row {
                spacing: 8
                Button {
                    text: "Start Training Session"
                    onClicked: {
                        if (guiBridge) {
                            guiBridge.sendCommand("start_training_session", "{}")
                        }
                    }
                }
                Button {
                    text: "End Training Session"
                    onClicked: {
                        if (guiBridge) {
                            guiBridge.sendCommand("end_training_session", "{}")
                        }
                    }
                }
                Button {
                    text: "Refresh Snapshot"
                    onClicked: {
                        if (guiBridge) {
                            guiBridge.sendCommand("refresh_snapshot", "{}")
                        }
                    }
                }
            }
        }

        GroupBox {
            width: parent.width
            title: "Debug Panel"
            Column {
                spacing: 8
                Row {
                    spacing: 8
                    Button {
                        text: "Start Mock Session (Debug)"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("start_mock_session", "{}")
                            }
                        }
                    }
                    Button {
                        text: "End Session"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("end_session", "{}")
                            }
                        }
                    }
                }
                Row {
                    spacing: 8
                    Button {
                        text: "Force L1"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("set_debug_difficulty", "{\"level\":1}")
                            }
                        }
                    }
                    Button {
                        text: "Force L2"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("set_debug_difficulty", "{\"level\":2}")
                            }
                        }
                    }
                    Button {
                        text: "Force L3"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("set_debug_difficulty", "{\"level\":3}")
                            }
                        }
                    }
                    Button {
                        text: "Force L4"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("set_debug_difficulty", "{\"level\":4}")
                            }
                        }
                    }
                    Button {
                        text: "Force L5"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("set_debug_difficulty", "{\"level\":5}")
                            }
                        }
                    }
                    Button {
                        text: "Auto DDA"
                        onClicked: {
                            if (guiBridge) {
                                guiBridge.sendCommand("set_debug_difficulty", "{\"level\":null}")
                            }
                        }
                    }
                }
            }
        }

        GroupBox {
            width: parent.width
            title: "Link Diagnostics"
            Label { text: "Link Diagnostics" }
        }

        GroupBox {
            width: parent.width
            title: "NAC / Live Status"
            Label { text: "NAC / Live Status" }
        }
    }
}
