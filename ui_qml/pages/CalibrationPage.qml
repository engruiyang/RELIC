import QtQuick
import QtQuick.Controls
import "../components"
Item { property var controlStateObj: ({}); property string commandSummary: ""; property string selectedCommandId: ""; property string selectedStatus: ""; property string selectedExecutionMode: ""; property string selectedNativeActionId: ""; signal invokeNative(string actionId)
 function pick(id,status,mode,native){ selectedCommandId=id; selectedStatus=status; selectedExecutionMode=mode; selectedNativeActionId=native; if (mode==="native"&&native!=="") invokeNative(native) }
 function s(v){return (v===undefined||v===null||v==="")?"n/a":String(v)}
 Column { anchors.fill: parent; spacing: 6
  PageHeader { titleText: "Calibration Page"; subtitleText: "Calibration management" }
  GroupBox { title: "Calibration Page Actions"; Column {
   Button { text: "Calibration Status"; onClicked: pick("calibration.status","native_ready","native","calibration.status") }
   Button { text: "List Calibrations"; onClicked: pick("calibration.list","active","copy_only","") }
   Button { text: "Latest Calibration"; onClicked: pick("calibration.latest","active","copy_only","") }
   Button { text: "Show Calibration"; onClicked: pick("calibration.show","active","copy_only","") }
   Button { text: "Bind Calibration"; onClicked: pick("calibration.bind","active","manual","") }
   Button { text: "Start First Profile Calibration"; enabled: false }
   Button { text: "Start Quick Check"; enabled: false }
   Button { text: "Cancel Calibration"; onClicked: pick("calibration.cancel","active","manual","") }
  }}
  GroupBox { title: "Calibration Modes"; Column { Label{text:"First Profile Calibration"}; Label{text:"Quick Check"}; Label{text:"Periodic Recalibration"}; Label{text:"Triggered Recalibration"} } }
  GroupBox { title: "Calibration Page Result"; Column { Label{text:"calibration_status: "+s(controlStateObj.calibration_status)}; Label{text:"last_calibration_id: "+s(controlStateObj.last_calibration_id)}; Label{text:"calibration_usable: "+s(controlStateObj.calibration_usable)}; Label{text:"latest_valid: "+s(controlStateObj.latest_valid)}; Label{text:"failure_reason: "+s(controlStateObj.failure_reason)}; Label{text:"source: "+s(controlStateObj.source)}; Label{text:"attention_baseline: "+s(controlStateObj.attention_baseline)}; Label{text:"gyro_noise_rms: "+s(controlStateObj.gyro_noise_rms)} } }
  GroupBox { title: "Page Commands"; Label { text: commandSummary; wrapMode: Text.WordWrap } }
  PageFeedbackPanel { pageId:"calibration"; selectedCommandId: parent.selectedCommandId; selectedStatus: parent.selectedStatus; selectedExecutionMode: parent.selectedExecutionMode; selectedNativeActionId: parent.selectedNativeActionId; lastCommand:s(controlStateObj.last_command); lastResult:s(controlStateObj.last_command_result); lastError:s(controlStateObj.last_command_error) }
 }}

// Page Feedback
