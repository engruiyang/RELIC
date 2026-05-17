from pathlib import Path

def test_app_shell_tokens_present() -> None:
    qml = Path('ui_qml/MinimalGui.qml').read_text(encoding='utf-8')
    for t in ['property string currentPage: "home"','home','user','calibration','training','report','diagnostics','Home','User','Calibration','Training','Report','Diagnostics','current_user_id','connection_status','quality_state','control_state','session_active','profile_status','calibration_status','latest_report_path','profile_loaded','user_type','attention_low_threshold','attention_high_threshold','preferred_game_id','calibration_usable','last_calibration_id','failure_reason','First Profile Calibration','Quick Check','Periodic Recalibration','Triggered Recalibration','GameCanvas will be restored in TASK24','score','combo','level','session_elapsed_ms','behavior_sample_count','Fragment Lock','Signal Hunter','Stabilizer','last_session_status','current_session_id','attention','gyro_x','sqi','fi_smoothed','warning_flags','error_flags']:
        assert t in qml
