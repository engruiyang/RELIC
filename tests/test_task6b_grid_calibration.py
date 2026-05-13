import json, subprocess, sys

def _prep(tmp_path):
    (tmp_path/'a.jsonl').write_text('\n'.join([
        json.dumps({"session_id":"distracted_to_focus_001","now_ms":1000,"attention":10,"attention_fresh":True,"gyro_fresh":True,"p_rate":0.1,"p_jitter":0.1,"p_offset":0.1}),
        json.dumps({"session_id":"distracted_to_focus_001","now_ms":2000,"attention":80,"attention_fresh":True,"gyro_fresh":True,"p_rate":0.1,"p_jitter":0.1,"p_offset":0.1}),
        json.dumps({"session_id":"gyro_motion_001","now_ms":1000,"attention":70,"attention_fresh":True,"gyro_fresh":True,"p_rate":0.95,"p_jitter":0.95,"p_offset":0.95}),
    ])+'\n',encoding='utf-8')
    (tmp_path/'a.frames.csv').write_text('session_id,frame_id,start_ms,end_ms,start_sec,end_sec,label,confidence,note\n'
                                     'distracted_to_focus_001,0,0,1500,0,1.5,DISTRACTED,low,\n'
                                     'distracted_to_focus_001,1,1500,2500,1.5,2.5,STABLE_FOCUS,low,\n'
                                     'gyro_motion_001,0,0,1500,0,1.5,UNRELIABLE_SIGNAL,low,\n',encoding='utf-8')
    (tmp_path/'cfg.json').write_text(json.dumps({"fi_ema_alpha":0.7,"attention_low_fallback":40,"attention_high_fallback":70,"stable_enter":60,"distracted_enter":50}),encoding='utf-8')

def test_help_runs():
    r=subprocess.run([sys.executable,'-m','ui_cli.grid_calibrate_task6b','-h'],check=True,capture_output=True,text=True)
    assert '--search-mode' in r.stdout and '--n-jobs' in r.stdout

def test_grid_v2_report_fields(tmp_path):
    _prep(tmp_path)
    out_cfg=tmp_path/'o.yaml'; report=tmp_path/'r.json'; mis=tmp_path/'m.csv'
    subprocess.run([sys.executable,'-m','ui_cli.grid_calibrate_task6b','--input',str(tmp_path/'*.jsonl'),'--labels',str(tmp_path/'*.frames.csv'),'--base-config',str(tmp_path/'cfg.json'),'--out-config',str(out_cfg),'--report',str(report),'--misclassified-out',str(mis),'--search-mode','coarse-to-fine','--max-combinations','5','--n-jobs','1'],check=True)
    rep=json.loads(report.read_text(encoding='utf-8')); cfg=json.loads(out_cfg.read_text(encoding='utf-8'))
    assert rep['search_summary']['total_combinations_evaluated']>0
    assert rep['reject_reasons'] or rep['acceptance_checks']
    if not rep['search_summary']['accepted']:
        assert rep['reject_reasons']
    assert 'tradeoff_analysis' in rep and 'folds' in rep['cross_validation_results']
    assert 'accepted' in cfg and 'experimental' in cfg and 'reject_reasons' in cfg
    assert 'max_combinations truncated search' in rep['warnings']
