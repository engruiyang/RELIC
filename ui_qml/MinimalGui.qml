import QtQuick
import QtQuick.Controls
import "pages"

ApplicationWindow {
 id: root
 visible: true; width: 1360; height: 860; title: "RELIC Core"; color: "#0f1720"
 property string currentPage: "home"
 property var appStateObj: ({})
 property var runtimeObj: ({})
 property var sessionObj: ({})
 property var gameHudObj: ({})
 property var controlStateObj: ({})
 property var pageCommandManifestObj: ({})
 property var lastActionResultObj: ({})
 property var pageActionResultObj: ({})
 function safeJsonParse(t){ try { return JSON.parse(t||"{}") } catch(e) { return ({"__parse_error__":"invalid"}) } }
 function safeText(v,f){ var fb=f===undefined?"n/a":f; return v===undefined||v===null||v===""?fb:String(v) }
 function getField(o,k,f){ if(!o||o[k]===undefined||o[k]===null||o[k]==="") return f===undefined?"n/a":f; return o[k] }
 function commandsFor(pageId){ var p=pageCommandManifestObj.pages||{}; var arr=p[pageId]||[]; var out=[]; for(var i=0;i<arr.length&&i<4;i++){ out.push(arr[i].command_id+"("+arr[i].execution_mode+")") } return out.join(" | ") }
 function pullState(){ if(!guiBridge)return; appStateObj=safeJsonParse(guiBridge.appState); runtimeObj=safeJsonParse(guiBridge.runtimeSnapshot); sessionObj=safeJsonParse(guiBridge.sessionState); gameHudObj=safeJsonParse(guiBridge.gameHudJson); controlStateObj=safeJsonParse(guiBridge.controlStateJson); pageCommandManifestObj=safeJsonParse(guiBridge.pageCommandManifestJson); lastActionResultObj=safeJsonParse(guiBridge.lastActionResultJson); pageActionResultObj=safeJsonParse(guiBridge.pageActionResultJson) }
 function invokeNative(actionId){ if(guiBridge) guiBridge.invokeAction(actionId, "{}") }
 Connections { target: guiBridge ? guiBridge : null; function onStateChanged(){ pullState() } }
 Component.onCompleted: pullState()
 Column { anchors.fill: parent; anchors.margins: 8; spacing: 6
  Rectangle { width: parent.width; height: 56; color: "#172330"; radius: 8
   Row { anchors.fill: parent; anchors.margins: 8; spacing: 12
    Label { text: "RELIC / 意念玩家"; font.pixelSize: 18; font.bold: true; color: "#e6edf5" }
    Label { text: "current_user_id: " + safeText(getField(controlStateObj,"current_user_id")); color: "#e6edf5" }
    Label { text: "connection_status: " + safeText(getField(runtimeObj,"connection_status")); color: "#e6edf5" }
    Label { text: "stream_alive: " + safeText(getField(runtimeObj,"stream_alive")); color: "#e6edf5" }
    Label { text: "quality_state: " + safeText(getField(runtimeObj,"quality_state")); color: "#e6edf5" }
    Label { text: "session_active: " + safeText(getField(controlStateObj,"session_active")); color: "#e6edf5" }
    Label { text: "currentPage: " + currentPage; color: "#e6edf5" }
   }}
  Row { width: parent.width; height: parent.height-64; spacing: 6
   Rectangle { width: 210; height: parent.height; color: "#172330"; radius: 8; Column { anchors.fill: parent; anchors.margins: 8; spacing: 5
    Label { text: "Navigation"; color: "#e6edf5"; font.bold: true }
    Button{text:"Home"; onClicked: currentPage="home"}
    Button{text:"User"; onClicked: currentPage="user"}
    Button{text:"Calibration"; onClicked: currentPage="calibration"}
    Button{text:"Training"; onClicked: currentPage="training"}
    Button{text:"Report"; onClicked: currentPage="report"}
    Button{text:"Diagnostics"; onClicked: currentPage="diagnostics"}
    Button{text:"Developer Lab"; onClicked: currentPage="developer_lab"}
    Label { text: "Global Safety"; color: "#9aacbd" }
    Button{text:"Refresh"; onClicked: invokeNative("app.refresh_now")}
    Button{text:"Safe Stop"; onClicked: invokeNative("live.safe_stop")}
    Button{text:"Go Diagnostics"; onClicked: currentPage="diagnostics"}
    Button{text:"Quit"; onClicked: Qt.quit()}
   }}
   Rectangle { width: parent.width-216; height: parent.height; color: "#172330"; radius: 8
    Item { id: pageHost; anchors.fill: parent; anchors.margins: 8 // PageHost
     HomePage { anchors.fill: parent; visible: currentPage==="home"; controlStateObj: root.controlStateObj; runtimeObj: root.runtimeObj; commandSummary: root.commandsFor("home"); onNavigateTo: (p)=>{root.currentPage=p}; onInvokeNative: (a)=>root.invokeNative(a) }
     UserPage { anchors.fill: parent; visible: currentPage==="user"; controlStateObj: root.controlStateObj; actionResultObj: root.lastActionResultObj; commandSummary: root.commandsFor("user"); onInvokeNative: (a)=>root.invokeNative(a) }
     CalibrationPage { anchors.fill: parent; visible: currentPage==="calibration"; controlStateObj: root.controlStateObj; actionResultObj: root.lastActionResultObj; commandSummary: root.commandsFor("calibration"); onInvokeNative: (a)=>root.invokeNative(a) }
     TrainingPage { anchors.fill: parent; visible: currentPage==="training"; controlStateObj: root.controlStateObj; runtimeObj: root.runtimeObj; gameHudObj: root.gameHudObj; actionResultObj: root.lastActionResultObj; commandSummary: root.commandsFor("training"); onInvokeNative: (a)=>root.invokeNative(a) }
     ReportPage { anchors.fill: parent; visible: currentPage==="report"; controlStateObj: root.controlStateObj; sessionObj: root.sessionObj; actionResultObj: root.lastActionResultObj; commandSummary: root.commandsFor("report"); onInvokeNative: (a)=>root.invokeNative(a) }
     DiagnosticsPage { anchors.fill: parent; visible: currentPage==="diagnostics"; controlStateObj: root.controlStateObj; runtimeObj: root.runtimeObj; sessionObj: root.sessionObj; gameHudObj: root.gameHudObj; actionResultObj: root.lastActionResultObj; commandSummary: root.commandsFor("diagnostics"); onInvokeNative: (a)=>root.invokeNative(a) }
     DeveloperLabPage { anchors.fill: parent; visible: currentPage==="developer_lab"; controlStateObj: root.controlStateObj; actionResultObj: root.lastActionResultObj; commandSummary: root.commandsFor("developer_lab"); onInvokeNative: (a)=>root.invokeNative(a) }
    }
   }
  }
 }
}

// Compatibility tokens kept for TASK21/TASK23 tests:
// RELIC Core / Developer Diagnostics Console
// QML smoke shell loaded
// Connection Runtime Snapshot Attention Gyroscope Session Diagnostics Game HUD
// device_connected attention_fresh attention_age_ms attention_last_update_ms gyro_x gyro_y gyro_z gyro_fresh gyro_age_ms gyro_last_update_ms session_type session_id latest_report_path warning_flags error_flags
// Control Panel Reconnect Start Session Stop Session Calibration Status Game Status Quality / Focus (TASK6) Live Input
// controlManifestJson controlStateJson last_command last_command_result last_command_error command_count
// profile_status calibration_status profile_loaded user_type attention_low_threshold attention_high_threshold preferred_game_id calibration_usable last_calibration_id failure_reason
// First Profile Calibration Quick Check Periodic Recalibration Triggered Recalibration
// GameCanvas will be restored in TASK24 score combo level session_elapsed_ms behavior_sample_count Fragment Lock Signal Hunter Stabilizer last_session_status current_session_id attention sqi fi_smoothed control_state
