import QtQuick
import QtQuick.Controls
import "../components"
Item {
 property var controlStateObj: ({})
 property string commandSummary: ""
 property string selectedCommandId: ""
 property string selectedStatus: ""
 property string selectedExecutionMode: ""
 property string selectedNativeActionId: ""
 signal invokeNative(string actionId)
 function pick(id,status,mode,native,cli){ selectedCommandId=id; selectedStatus=status; selectedExecutionMode=mode; selectedNativeActionId=native; if (mode==="native"&&native!=="") invokeNative(native) }
 function safeText(v){ return (v===undefined||v===null||v==="")?"n/a":String(v) }
 Column { anchors.fill: parent; spacing: 6
  PageHeader { titleText: "User Page"; subtitleText: "User/Profile actions" }
  GroupBox { title: "User Page Actions"; Column {
   Button { text: "List Users"; onClicked: pick("user.list","active","copy_only","","python -m ui_cli.run_user_debug --list-users") }
   Button { text: "Create User"; onClicked: pick("user.create","active","manual","","") }
   Button { text: "Load User"; onClicked: pick("user.load","active","manual","","") }
   Button { text: "Load Current User"; onClicked: pick("user.load_current","native_ready","native","user.load_current","") }
   Button { text: "Show Profile"; onClicked: pick("user.show_profile","native_ready","native","user.show_profile","") }
   Button { text: "Guest Mode"; onClicked: pick("user.guest","active","manual","","") }
   Button { text: "Ensure Demo Debug"; onClicked: pick("user.load_demo_debug","active","manual","","") }
  }}
  GroupBox { title: "User Page Result"; Column {
    Label { text: "current_user_id: " + safeText(controlStateObj.current_user_id) }
    Label { text: "user_type: " + safeText(controlStateObj.user_type) }
    Label { text: "profile_loaded: " + safeText(controlStateObj.profile_loaded) }
    Label { text: "profile_status: " + safeText(controlStateObj.profile_status) }
    Label { text: "last_calibration_id: " + safeText(controlStateObj.last_calibration_id) }
    Label { text: "attention_low_threshold: " + safeText(controlStateObj.attention_low_threshold) }
    Label { text: "attention_high_threshold: " + safeText(controlStateObj.attention_high_threshold) }
    Label { text: "preferred_game_id: " + safeText(controlStateObj.preferred_game_id) }
    Label { text: "difficulty_level: " + safeText(controlStateObj.difficulty_level) }
  }}
  GroupBox { title: "Page Commands"; Label { text: commandSummary; wrapMode: Text.WordWrap } }
  PageFeedbackPanel { pageId: "user"; selectedCommandId: parent.selectedCommandId; selectedStatus: parent.selectedStatus; selectedExecutionMode: parent.selectedExecutionMode; selectedNativeActionId: parent.selectedNativeActionId; lastCommand: safeText(controlStateObj.last_command); lastResult: safeText(controlStateObj.last_command_result); lastError: safeText(controlStateObj.last_command_error) }
 }
}

// Page Feedback
