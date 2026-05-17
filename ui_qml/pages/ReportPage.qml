import QtQuick
import QtQuick.Controls
import "../components"
Item { property var controlStateObj: ({}); property var sessionObj: ({}); property string commandSummary:""; property string selectedCommandId:""; property string selectedStatus:""; property string selectedExecutionMode:""; property string selectedNativeActionId:"";
 function pick(id,status,mode,native){ selectedCommandId=id; selectedStatus=status; selectedExecutionMode=mode; selectedNativeActionId=native }
 function s(v){return (v===undefined||v===null||v==="")?"n/a":String(v)}
 Column { anchors.fill: parent; spacing:6
  PageHeader { titleText:"Report Page"; subtitleText:"Report/session summary" }
  GroupBox { title:"Report Page Actions"; Row{ spacing:4
   Button{text:"List Sessions"; onClicked: pick("report.list_sessions","active","copy_only","")}
   Button{text:"Show Session"; onClicked: pick("report.show_session","active","copy_only","")}
   Button{text:"Latest Report"; onClicked: pick("report.latest","active","manual","")}
   Button{text:"Replay Summary"; enabled:false}
   Button{text:"Open Path Manual"; onClicked: pick("report.open_path_manual","manual","manual","")}
  }}
  GroupBox { title:"Report State"; Column { Label{text:"latest_report_path: "+s(controlStateObj.latest_report_path)}; Label{text:"last_session_status: "+s(controlStateObj.last_session_status)}; Label{text:"current_session_id: "+s(controlStateObj.current_session_id)}; Label{text:"session_active: "+s(controlStateObj.session_active)}; Label{text:"report_status: "+s(controlStateObj.report_status)}; Label{text:"log_path: "+s(controlStateObj.log_path)}; Label{text:"game_event_count: "+s(controlStateObj.game_event_count)}; Label{text:"behavior_sample_count: "+s(sessionObj.behavior_sample_count)} } }
  Label { text: "Full report viewer will be handled in later tasks." }
  GroupBox { title:"Page Commands"; Label{text:commandSummary; wrapMode: Text.WordWrap} }
  PageFeedbackPanel { pageId:"report"; selectedCommandId: parent.selectedCommandId; selectedStatus: parent.selectedStatus; selectedExecutionMode: parent.selectedExecutionMode; selectedNativeActionId: parent.selectedNativeActionId; lastCommand:s(controlStateObj.last_command); lastResult:s(controlStateObj.last_command_result); lastError:s(controlStateObj.last_command_error) }
 }}

// Page Feedback
