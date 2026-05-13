from __future__ import annotations

def predict_task6b_frame(row, params, prev_state=None, runtime_state=None):
    runtime_state = runtime_state or {}
    motion_mode = params.get('motion_score_mode', 'max')
    rw = params.get('rate_weight', 1.0); jw = params.get('jitter_weight', 1.0); ow = params.get('offset_weight', 1.0)
    pr = float(row.get('p_rate', 0) or 0); pj = float(row.get('p_jitter', 0) or 0); po = float(row.get('p_offset', 0) or 0)
    motion = max(pr*rw, pj*jw, po*ow) if motion_mode == 'max' else min(1.0, max(0.0, pr*rw + pj*jw + po*ow))
    att = row.get('attention')
    gate = (att is None) or (not row.get('attention_fresh', True)) or (not row.get('gyro_fresh', True)) or motion >= params.get('motion_unreliable_threshold', 0.8)
    if gate:
        return {'predicted_label':'UNRELIABLE_SIGNAL','fi_raw':0.0,'fi_smoothed':0.0,'motion_score':motion,'reliability_reason':'gate','gate_triggered':True,'decision_reason':'reliability_gate'}
    att_low=params.get('attention_low',40); att_high=params.get('attention_high',70)
    s_att=max(0,min(1,(float(att)-att_low)/max(att_high-att_low,1e-6)))*100
    fi_raw=0.85*s_att+params.get('motion_penalty_weight',0.2)*(100*(1-max(0,min(1,motion))))
    prev_fi = runtime_state.get('fi')
    if prev_fi is None or params.get('ema_warmup_strategy')=='first_frame_raw': prev_fi = fi_raw
    alpha=params.get('fi_ema_alpha',0.7)
    fi_sm = alpha*fi_raw + (1-alpha)*prev_fi
    runtime_state['fi']=fi_sm
    state = runtime_state.get('state', prev_state or 'DISTRACTED')
    se = runtime_state.get('se',0)+1 if fi_sm >= params.get('stable_enter',60) else 0
    de = runtime_state.get('de',0)+1 if fi_sm <= params.get('distracted_enter',50) else 0
    runtime_state['se']=se; runtime_state['de']=de
    if se >= params.get('stable_enter_count',1): pred='STABLE_FOCUS'
    elif de >= params.get('distracted_enter_count',1): pred='DISTRACTED'
    else:
        pred='STABLE_FOCUS' if fi_sm >= (params.get('stable_enter',60)+params.get('distracted_enter',50))/2 else 'DISTRACTED'
        if params.get('state_hold_strategy','none')!='none' and runtime_state.get('dur',0)<params.get('min_state_duration_frames',1): pred=state
    runtime_state['dur']=runtime_state.get('dur',0)+1 if pred==state else 1
    runtime_state['state']=pred
    return {'predicted_label':pred,'fi_raw':fi_raw,'fi_smoothed':fi_sm,'motion_score':motion,'reliability_reason':'ok','gate_triggered':False,'decision_reason':'fi_path'}
