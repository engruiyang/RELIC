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
    it=mod._build_ds([],[])
    assert not isinstance(it,list)

def test_staged_grid_report(tmp_path):
    prep(tmp_path)
    out_cfg=tmp_path/'o.json'; rep=tmp_path/'r.json'; mis=tmp_path/'m.csv'; clog=tmp_path/'c.jsonl'
    subprocess.run([sys.executable,'-m','ui_cli.grid_calibrate_task6b','--optimizer','staged_grid','--search-mode','staged','--input',str(tmp_path/'*.jsonl'),'--labels',str(tmp_path/'*.frames.csv'),'--base-config',str(tmp_path/'cfg.json'),'--out-config',str(out_cfg),'--report',str(rep),'--misclassified-out',str(mis),'--stage1-max-combinations','50','--stage2-max-combinations','50','--stage3-max-combinations','50','--candidate-log',str(clog)],check=True)
    r=json.loads(rep.read_text()); c=json.loads(out_cfg.read_text())
    assert 'stage1_gate_search' in r and 'stage2_fi_search' in r and 'stage3_transition_search' in r
    assert r['accepted'] == r['search_summary']['accepted'] == c['accepted']
    assert all(x in r['acceptance_checks'] for x in ['unreliable_miss_not_worse'])
    assert all(not rr.startswith('score_improved') for rr in r['reject_reasons'])
    assert set(r['failed_checks']).issubset({k for k,v in r['acceptance_checks'].items() if not v})
    assert r['memory_report']
