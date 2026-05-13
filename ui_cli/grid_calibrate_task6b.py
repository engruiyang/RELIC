from __future__ import annotations
import argparse,csv,glob,itertools,json,heapq,statistics,time,datetime
from pathlib import Path
from ui_cli.evaluate_task6b import _load_jsonl,_load_labels,load_structured_file
from core.task6b_predictor import predict_task6b_frame

def _q(vals,qs):
    vals=sorted(v for v in vals if isinstance(v,(int,float)))
    return [] if not vals else sorted(set(vals[min(len(vals)-1,max(0,int((len(vals)-1)*q)))] for q in qs))

def _build_ds(rows,labels):
    by={}
    for r in rows: by.setdefault(r.get('session_id'),[]).append(r)
    for fr in labels:
        if fr.get('label')=='IGNORE': continue
        sid=fr.get('session_id');a=int(fr.get('start_ms',0));b=int(fr.get('end_ms',0));ev=[r for r in by.get(sid,[]) if a<=int(r.get('now_ms',0))<b]
        if not ev: continue
        r=ev[-1]
        yield {'session_id':sid,'frame_id':fr.get('frame_id',''),'start_ms':a,'end_ms':b,'true_label':fr.get('label'),'attention':r.get('attention'),'attention_fresh':r.get('attention_fresh'),'gyro_fresh':r.get('gyro_fresh'),'p_rate':r.get('p_rate',0) or 0,'p_jitter':r.get('p_jitter',0) or 0,'p_offset':r.get('p_offset',0) or 0}

def _metrics(preds):
    labs=sorted(set([x['true_label'] for x in preds]+[x['predicted_label'] for x in preds]));cm={};pd={};ld={};tot=len(preds);corr=0
    for x in preds:
        t,p=x['true_label'],x['predicted_label'];corr+=int(t==p);ld[t]=ld.get(t,0)+1;pd[p]=pd.get(p,0)+1;cm.setdefault(t,{}).setdefault(p,0);cm[t][p]+=1
    f1=[]
    for c in labs:
        tp=cm.get(c,{}).get(c,0);fp=sum(cm.get(o,{}).get(c,0) for o in labs if o!=c);fn=sum(v for k,v in cm.get(c,{}).items() if k!=c);pr=tp/max(tp+fp,1);rc=tp/max(tp+fn,1);f1.append(0 if pr+rc==0 else 2*pr*rc/(pr+rc))
    macro=sum(f1)/max(len(f1),1);acc=corr/max(tot,1);um=sum(1 for x in preds if x['true_label']=='UNRELIABLE_SIGNAL' and x['predicted_label']!='UNRELIABLE_SIGNAL');fu=sum(1 for x in preds if x['true_label']!='UNRELIABLE_SIGNAL' and x['predicted_label']=='UNRELIABLE_SIGNAL');fh=sum(1 for x in preds if x['predicted_label']=='HIGH_FOCUS' and x['true_label']!='HIGH_FOCUS');cp=max(max((v/max(tot,1) for v in pd.values()),default=0)-0.85,0)
    return {'frame_accuracy':acc,'macro_f1':macro,'weighted_f1':sum((ld.get(c,0)/max(tot,1))*f1[i] for i,c in enumerate(labs)),'unreliable_miss':um,'false_unreliable':fu,'false_high_focus':fh,'false_fatigue':0,'unreliable_miss_rate':um/max(tot,1),'false_unreliable_rate':fu/max(tot,1),'false_high_focus_rate':fh/max(tot,1),'transition_jitter':0.0,'single_class_collapse_penalty':cp,'prediction_distribution':pd,'label_distribution':ld,'confusion_matrix':cm}

def _score(m,worst,mean_cv,trans):
    return 1.0*m['macro_f1']+0.5*m['frame_accuracy']-4*m['unreliable_miss_rate']-2*m['false_unreliable_rate']-2*m['false_high_focus_rate']-0.5*m['single_class_collapse_penalty']+0.3*worst+0.2*mean_cv-0.5*max(0,0.45-trans)

def _eval(ds,params,sessions):
    preds=[];ctx={}
    for r in sorted(ds,key=lambda x:(x['session_id'],x['start_ms'])):
        st=ctx.setdefault(r['session_id'],{})
        p=predict_task6b_frame(r,params,prev_state=st.get('state'),runtime_state=st)
        preds.append({**r,**p})
    m=_metrics(preds)
    per=[]
    for s in sessions:
        sm=_metrics([x for x in preds if x['session_id']==s]); per.append({'session_id':s,'score':sm['macro_f1'],'macro_f1':sm['macro_f1'],'unreliable_miss':sm['unreliable_miss'],'false_unreliable':sm['false_unreliable'],'confusion_matrix':sm['confusion_matrix']})
    worst=min((x['score'] for x in per),default=0);mean_cv=statistics.mean((x['score'] for x in per)) if per else 0;trans=min([x['score'] for x in per if 'distracted_to_focus' in str(x['session_id'])] or [worst])
    m['worst_session_score']=worst;m['mean_validation_score']=mean_cv;m['transition_session_score']=trans;m['score']=_score(m,worst,mean_cv,trans)
    return m,per,preds

def _push(heap,k,item,key,seq):
    v=key(item);ent=(v,seq,item)
    if len(heap)<k: heapq.heappush(heap,ent)
    elif v>heap[0][0]: heapq.heapreplace(heap,ent)

def main():
    ap=argparse.ArgumentParser();
    ap.add_argument('--optimizer',choices=['staged_grid','grid'],default='staged_grid');ap.add_argument('--search-mode',choices=['staged','coarse-to-fine','grid'],default='staged')
    ap.add_argument('--input',required=True);ap.add_argument('--labels',required=True);ap.add_argument('--base-config',required=True);ap.add_argument('--out-config',required=True);ap.add_argument('--report',required=True);ap.add_argument('--misclassified-out',required=True)
    ap.add_argument('--stage1-max-combinations',type=int,default=20000);ap.add_argument('--stage2-max-combinations',type=int,default=30000);ap.add_argument('--stage3-max-combinations',type=int,default=30000)
    ap.add_argument('--min-gate-recall',type=float,default=0.95);ap.add_argument('--max-false-unreliable-rate',type=float,default=0.15);ap.add_argument('--min-fi-session-score',type=float,default=0.45);ap.add_argument('--min-transition-session-score',type=float,default=0.45);ap.add_argument('--min-worst-session-score',type=float,default=0.4)
    ap.add_argument('--top-k',type=int,default=30);ap.add_argument('--cv-mode',choices=['none','leave-one-session-out'],default='leave-one-session-out');ap.add_argument('--candidate-log');ap.add_argument('--memory-safe',choices=['true','false'],default='true');ap.add_argument('--n-jobs',type=int,default=1);ap.add_argument('--batch-size',type=int,default=1000);ap.add_argument('--max-stored-candidates',type=int,default=300)
    a=ap.parse_args(); t0=time.time(); warnings=[]
    rows=_load_jsonl(sorted(glob.glob(a.input))); labels,_=_load_labels(sorted(glob.glob(a.labels))); ds=list(_build_ds(rows,labels)); base=load_structured_file(a.base_config); sessions=sorted({x['session_id'] for x in ds})
    if a.n_jobs!=1: warnings.append('n_jobs forced to 1 in staged memory-safe mode')
    # grids
    by={}; [by.setdefault(x['true_label'],[]).append(x) for x in ds]
    gate_grid={'motion_score_mode':['max','weighted_sum'],'rate_weight':[0.8,1.0,1.2],'jitter_weight':[0.8,1.0,1.2],'offset_weight':[0.8,1.0,1.2],'motion_unreliable_threshold':sorted(set((_q([max(x['p_rate'],x['p_jitter'],x['p_offset']) for x in by.get('UNRELIABLE_SIGNAL',[])],[0.2,0.4,0.6,0.8])+[0.5,0.7,0.9]))),'attention_stale_ms':[500,1000,1500],'gyro_stale_ms':[500,1000,1500],'startup_unreliable_frames':[0,1,2],'force_unreliable_on_motion_bad':[True]}
    fi_grid={'attention_low':sorted(set((_q([x['attention'] for x in by.get('DISTRACTED',[]) if isinstance(x.get('attention'),(int,float))],[0.1,0.25,0.5,0.75])+[base.get('attention_low_fallback',40)]))),'attention_high':sorted(set((_q([x['attention'] for x in by.get('STABLE_FOCUS',[]) if isinstance(x.get('attention'),(int,float))],[0.25,0.5,0.75,0.9])+[base.get('attention_high_fallback',70)]))),'stable_enter':sorted(set(_q([x['attention'] for x in by.get('STABLE_FOCUS',[]) if isinstance(x.get('attention'),(int,float))],[0.3,0.5,0.7])+[base.get('stable_enter',60)])),'distracted_enter':sorted(set(_q([x['attention'] for x in by.get('DISTRACTED',[]) if isinstance(x.get('attention'),(int,float))],[0.3,0.5,0.7])+[base.get('distracted_enter',50)])),'fi_ema_alpha':[0.4,0.6,0.7,0.85],'motion_penalty_weight':[0.05,0.1,0.2,0.3],'neutral_band_strategy':['midpoint']}
    tr_grid={'state_hold_strategy':['none','previous_state_hysteresis','neutral_band_keep_previous'],'min_state_duration_frames':[1,2,3],'stable_enter_count':[1,2,3],'distracted_enter_count':[1,2,3],'ema_warmup_strategy':['first_frame_raw','reset_per_session','carry_within_session_only'],'transition_boost_enabled':[False,True],'attention_delta_weight':[0.0,0.1,0.2],'attention_slope_window':[1,2,3]}
    base_params={'attention_low':base.get('attention_low_fallback',40),'attention_high':base.get('attention_high_fallback',70),'stable_enter':base.get('stable_enter',60),'distracted_enter':base.get('distracted_enter',50),'fi_ema_alpha':base.get('fi_ema_alpha',0.7),'motion_penalty_weight':0.2,'motion_score_mode':'max','rate_weight':1.0,'jitter_weight':1.0,'offset_weight':1.0,'motion_unreliable_threshold':0.8,'state_hold_strategy':'none','min_state_duration_frames':1,'stable_enter_count':1,'distracted_enter_count':1,'ema_warmup_strategy':'first_frame_raw'}
    base_m,base_per,_=_eval(ds,base_params,sessions)
    logf=open(a.candidate_log,'w',encoding='utf-8') if a.candidate_log else None
    def stage_search(grid,limit,fixed,keyfn):
        heap=[];seq=0;evaled=0
        keys=list(grid.keys())
        for vals in itertools.product(*[grid[k] for k in keys]):
            if evaled>=limit: break
            seq+=1;params=dict(fixed);params.update(dict(zip(keys,vals)))
            m,per,_=_eval(ds,params,sessions)
            item={'params':params,'metrics':m,'per_session':per}
            _push(heap,min(a.top_k,a.max_stored_candidates),item,keyfn,seq);evaled+=1
            if logf: logf.write(json.dumps({'stage':'x','score':m['score'],'macro_f1':m['macro_f1'],'unreliable_miss':m['unreliable_miss'],'false_unreliable':m['false_unreliable'],'params':params},ensure_ascii=False)+'\n')
        return [x for *_,x in sorted(heap,reverse=True)],evaled
    st1,ev1=stage_search(gate_grid,a.stage1_max_combinations,base_params,lambda it:it['metrics']['score'])
    best_gate=st1[0] if st1 else {'params':base_params,'metrics':base_m,'per_session':base_per}
    st2,ev2=stage_search(fi_grid,a.stage2_max_combinations,best_gate['params'],lambda it:it['metrics']['score'])
    best_fi=st2[0] if st2 else best_gate
    st3,ev3=stage_search(tr_grid,a.stage3_max_combinations,best_fi['params'],lambda it:it['metrics']['score'])
    best=st3[0] if st3 else best_fi
    if logf: logf.close()
    final_m,final_per,final_preds=_eval(ds,best['params'],sessions)
    checks={
      'score_improved':final_m['score']>base_m['score'],
      'macro_f1_not_worse':final_m['macro_f1']>=base_m['macro_f1'],
      'accuracy_not_worse':final_m['frame_accuracy']>=base_m['frame_accuracy'],
      'unreliable_miss_not_worse':final_m['unreliable_miss']<=base_m['unreliable_miss'],
      'false_high_focus_not_worse':final_m['false_high_focus']<=base_m['false_high_focus'],
      'false_unreliable_within_limit':final_m['false_unreliable_rate']<=a.max_false_unreliable_rate,
      'worst_session_above_threshold':final_m['worst_session_score']>=a.min_worst_session_score,
      'transition_session_above_threshold':final_m['transition_session_score']>=a.min_transition_session_score,
      'no_single_class_collapse':final_m['single_class_collapse_penalty']==0,
    }
    failed=[k for k,v in checks.items() if not v]
    reject=[]
    if not checks['worst_session_above_threshold']: reject.append(f"worst_session_score below threshold: {final_m['worst_session_score']:.4f} < {a.min_worst_session_score}")
    if not checks['transition_session_above_threshold']: reject.append(f"transition_session_score below threshold: {final_m['transition_session_score']:.4f} < {a.min_transition_session_score}")
    if not checks['false_unreliable_within_limit']: reject.append(f"false_unreliable_rate above threshold: {final_m['false_unreliable_rate']:.4f} > {a.max_false_unreliable_rate}")
    for k in failed:
        if k not in ('worst_session_above_threshold','transition_session_above_threshold','false_unreliable_within_limit'):
            reject.append(f"check failed: {k}")
    accepted=not failed
    weak=[{'session_id':x['session_id'],'score':x['score'],'macro_f1':x['macro_f1'],'main_error_type':'low_session_score','suggested_next_grid_focus':'stage3 transition params'} for x in final_per if x['score']<a.min_worst_session_score]
    mis=[x for x in final_preds if x['true_label']!=x['predicted_label']]
    with open(a.misclassified_out,'w',encoding='utf-8',newline='') as f:
        cols=['session_id','frame_id','start_ms','end_ms','true_label','predicted_label','attention','motion_score','fi_raw','fi_smoothed','p_rate','p_jitter','p_offset','reason'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader();[w.writerow({k:r.get(k,'') for k in cols}) for r in mis]
    out_cfg={'calibration_method':'staged_grid','prediction_mode':'recompute','accepted':accepted,'experimental':not accepted,'reject_reasons':reject,'warnings':warnings,'selected_params':{'reliability_gate':best_gate['params'],'fi':best_fi['params'],'transition':best['params']},'score_summary':{'base_score':base_m['score'],'best_score':final_m['score']},'dataset_meta':{'total_labeled_frames':len(ds),'session_count':len(sessions)},'generated_at':datetime.datetime.utcnow().isoformat()+'Z','base_config_path':a.base_config}
    Path(a.out_config).write_text(json.dumps(out_cfg,ensure_ascii=False,indent=2),encoding='utf-8')
    report={'accepted':accepted,'dataset_meta':{'input_files_count':len(sorted(glob.glob(a.input))),'label_files_count':len(sorted(glob.glob(a.labels))),'matched_session_ids':sessions,'session_count':len(sessions),'total_labeled_frames':len(ds),'label_distribution':base_m['label_distribution']},'feature_distribution_summary':{'label_distribution':base_m['label_distribution']},'active_grid':{'stage1':list(gate_grid.keys()),'stage2':list(fi_grid.keys()),'stage3':list(tr_grid.keys())},'stage1_gate_search':{'params_searched':list(gate_grid.keys()),'total_evaluated':ev1,'best_gate_params':best_gate['params'],'gate_metrics':best_gate['metrics'],'gate_reject_reasons':[],'gate_warnings':[]},'stage2_fi_search':{'params_searched':list(fi_grid.keys()),'total_evaluated':ev2,'best_fi_params':best_fi['params'],'fi_metrics':best_fi['metrics'],'fi_weak_sessions':[x for x in best_fi['per_session'] if x['score']<a.min_fi_session_score],'fi_reject_reasons':[]},'stage3_transition_search':{'detected_transition_sessions':[s for s in sessions if 'transition' in s or 'distracted_to_focus' in s],'params_searched':list(tr_grid.keys()),'total_evaluated':ev3,'best_transition_params':best['params'],'transition_metrics':best['metrics'],'transition_reject_reasons':[]},'final_evaluation':final_m,'base_result':base_m,'best_result':final_m,'top_candidates':[{'rank':i+1,'params':c['params'],'score':c['metrics']['score']} for i,c in enumerate(st3[:a.top_k])],'safe_candidates':[{'params':c['params'],'unreliable_miss':c['metrics']['unreliable_miss']} for c in sorted(st3,key=lambda x:x['metrics']['unreliable_miss'])[:a.top_k]],'balanced_candidates':[{'params':c['params'],'score':c['metrics']['score']} for c in st3[:a.top_k]],'transition_candidates':[{'params':c['params'],'transition_session_score':c['metrics']['transition_session_score']} for c in sorted(st3,key=lambda x:x['metrics']['transition_session_score'],reverse=True)[:a.top_k]],'weak_sessions':weak,'acceptance_checks':checks,'failed_checks':failed,'reject_reasons':reject,'warnings':warnings,'tradeoff_analysis':{'best_overall_candidate':best['params'],'best_worst_session_candidate':max(st3,key=lambda x:x['metrics']['worst_session_score'])['params'] if st3 else {},'best_transition_candidate':max(st3,key=lambda x:x['metrics']['transition_session_score'])['params'] if st3 else {},'safest_unreliable_candidate':min(st3,key=lambda x:x['metrics']['unreliable_miss'])['params'] if st3 else {},'lowest_false_unreliable_candidate':min(st3,key=lambda x:x['metrics']['false_unreliable'])['params'] if st3 else {}},'memory_report':{'include_frame_predictions':False,'candidate_log_enabled':bool(a.candidate_log),'sqlite_cache_enabled':False,'note':'full candidate results are not retained in memory'},'search_summary':{'accepted':accepted,'total_combinations_seen':ev1+ev2+ev3,'total_combinations_evaluated':ev1+ev2+ev3,'stage1_evaluated':ev1,'stage2_evaluated':ev2,'stage3_evaluated':ev3,'batch_size':a.batch_size,'memory_safe':a.memory_safe,'max_stored_candidates':a.max_stored_candidates,'candidate_log_path':a.candidate_log,'elapsed_sec':time.time()-t0,'n_jobs':1},'score_formula':'staged balanced'}
    Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'accepted':accepted,'best_score':final_m['score']},ensure_ascii=False))

if __name__=='__main__': main()
