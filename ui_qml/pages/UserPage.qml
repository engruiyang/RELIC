import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    objectName: "UserPage"
    property var debugVisibleTokens: ["user", "userSummaryPanel", "userFormPanel", "userListPanel", "userDetailPanel", "userResultPanel"]
    property var controlStateObj: ({})
    property string commandSummary: ""
    property var actionResultObj: ({})
    signal invokeNative(string actionId)
    function s(v){ return (v===undefined||v===null||v==="")?"n/a":String(v) }
    Column { anchors.fill: parent; spacing: 6
        PageHeader { titleText: "User Page"; subtitleText: "Manage profile and current user context" }
        GroupBox { objectName: "userSummaryPanel"; title: "Current User Summary"; width: parent.width; Column {
            Label { text: "current_user_id: " + s(controlStateObj.current_user_id) }
            Label { text: "profile_status: " + s(controlStateObj.profile_status) }
            Label { text: "user_type: " + s(controlStateObj.user_type) }
        }}
        GroupBox { objectName: "userFormPanel"; title: "User Actions"; width: parent.width; Row { spacing: 6
            Button { text: "List Users"; onClicked: invokeNative("user.list") }
            Button { text: "Create User"; onClicked: invokeNative("user.create") }
            Button { text: "Load User"; onClicked: invokeNative("user.load") }
            Button { text: "Load Current"; onClicked: invokeNative("user.load_current") }
        }}
        GroupBox { objectName: "userListPanel"; title: "User List"; width: parent.width; PageListPanel { width: parent.width; height: 90; items: (actionResultObj.items || []) } }
        GroupBox { objectName: "userDetailPanel"; title: "User Detail"; width: parent.width; PageDetailPanel { width: parent.width; height: 90; detailObj: (actionResultObj.detail || {}) } }
        GroupBox { objectName: "userResultPanel"; title: "User Action Result"; width: parent.width; Column {
            Label { text: "empty_state: No user action result yet." }
            PageResultPanel { width: parent.width; actionResult: (actionResultObj || {"status":"n/a"}) }
        }}
        GroupBox { title: "Page Commands"; Label { text: commandSummary; wrapMode: Text.WordWrap } }

        // Page Feedback
    }
}
