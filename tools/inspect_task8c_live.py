from __future__ import annotations
import json, sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/inspect_task8c_live.py <pipeline_jsonl>")
        return 2
    p = Path(sys.argv[1])
    lines = [ln for ln in p.read_text(encoding='utf-8').splitlines() if ln.strip()]
    ticks=[]
    for ln in lines:
        try:
            rec=json.loads(ln)
        except Exception:
            continue
        if isinstance(rec,dict) and 'input' in rec and 'output' in rec:
            ticks.append(rec)
    tick_count=len(ticks)
    quality_states={}
    control_states={}
    fallback_count=cal_loaded=cal_usable=est_allowed=fi_valid=behavior_ticks=0
    score_last=0.0
    for t in ticks:
        i=t.get('input',{})
        o=t.get('output',{})
        q=i.get('quality_state'); c=i.get('control_state')
        quality_states[q]=quality_states.get(q,0)+1
        control_states[c]=control_states.get(c,0)+1
        fallback_count += 1 if i.get('provider_fallback_used') else 0
        cal_loaded += 1 if i.get('calibration_loaded') else 0
        cal_usable += 1 if i.get('calibration_usable') else 0
        est_allowed += 1 if i.get('estimation_allowed') else 0
        fi_valid += 1 if i.get('fi_valid') else 0
        behavior_ticks += 1 if o.get('behavior_sample_count',0)>0 else 0
        if o.get('score') is not None:
            score_last=float(o.get('score') or 0.0)
    verdict = 'PASS' if tick_count>0 and fallback_count==0 and fi_valid>0 and behavior_ticks>0 and score_last>0 else 'FAIL'
    print(f"tick_count={tick_count}")
    print(f"quality_states={quality_states}")
    print(f"control_states={control_states}")
    print(f"fallback_count={fallback_count}")
    print(f"calibration_loaded_count={cal_loaded}")
    print(f"calibration_usable_count={cal_usable}")
    print(f"estimation_allowed_count={est_allowed}")
    print(f"fi_valid_count={fi_valid}")
    print(f"behavior_tick_count={behavior_ticks}")
    print(f"score_last={score_last}")
    print(f"Final Verdict={verdict}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
