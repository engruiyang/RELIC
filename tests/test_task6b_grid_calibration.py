import json, subprocess, sys
from ui_cli import grid_calibrate_task6b as mod

def prep(tmp_path):
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

def test_generator_not_list():
    g={'a':[1,2],'b':[3,4]}
    it=mod._candidate_iter(g,10)
    assert not isinstance(it,list)

def test_v3_smoke(tmp_path):
    prep(tmp_path)
    out_cfg=tmp_path/'o.json'; rep=tmp_path/'r.json'; mis=tmp_path/'m.csv'; clog=tmp_path/'c.jsonl'
    subprocess.run([sys.executable,'-m','ui_cli.grid_calibrate_task6b','--input',str(tmp_path/'*.jsonl'),'--labels',str(tmp_path/'*.frames.csv'),'--base-config',str(tmp_path/'cfg.json'),'--out-config',str(out_cfg),'--report',str(rep),'--misclassified-out',str(mis),'--max-combinations','10','--batch-size','2','--max-stored-candidates','5','--candidate-log',str(clog),'--n-jobs','1'],check=True)
    r=json.loads(rep.read_text()); c=json.loads(out_cfg.read_text())
    assert r['search_summary']['candidates_stored'] <= r['search_summary']['max_stored_candidates']
    assert 'frame_predictions' not in r.get('best_result',{})
    assert clog.exists() and clog.read_text().strip()
    assert r['memory_report']['note']
    if not c['accepted']: assert c['reject_reasons']
    assert 'tradeoff_analysis' in r and 'folds' in r['cross_validation_results']

def test_memorysafe_njobs_guard(tmp_path):
    prep(tmp_path)
    out_cfg=tmp_path/'o.json'; rep=tmp_path/'r.json'; mis=tmp_path/'m.csv'
    p=subprocess.run([sys.executable,'-m','ui_cli.grid_calibrate_task6b','--input',str(tmp_path/'*.jsonl'),'--labels',str(tmp_path/'*.frames.csv'),'--base-config',str(tmp_path/'cfg.json'),'--out-config',str(out_cfg),'--report',str(rep),'--misclassified-out',str(mis),'--n-jobs','5'],capture_output=True,text=True)
    assert p.returncode != 0
