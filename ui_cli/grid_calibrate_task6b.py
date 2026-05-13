from __future__ import annotations
import argparse,csv,glob,itertools,json,statistics,time,datetime,multiprocessing as mp
from pathlib import Path
from ui_cli.evaluate_task6b import _load_jsonl,_load_labels,load_structured_file

def q(vals,qs):
    vals=sorted(v for v in vals if isinstance(v,(int,float)))
    if not vals:return []
    return sorted(set(vals[min(len(vals)-1,max(0,int((len(vals)-1)*x)))] for x in qs))

def build_ds(rows,labels):
    by={}
    for r in rows:by.setdefault(r.get('session_id'),[]).append(r)
    out=[]
    for fr in labels:
        if fr.get('label')=='IGNORE':continue
        sid=fr.get('session_id');a=int(fr.get('start_ms',0));b=int(fr.get('end_ms',0));ev=[r for r in by.get(sid,[]) if a<=int(r.get('now_ms',0))<b]
        if not ev:continue
        r=ev[-1]
        out.append({'session_id':sid,'frame_id':fr.get('frame_id',''),'start_ms':a,'end_ms':b,'true_label':fr.get('label'),'attention':r.get('attention'),'attention_fresh':r.get('attention_fresh'),'gyro_fresh':r.get('gyro_fresh'),'p_rate':r.get('p_rate',0) or 0,'p_jitter':r.get('p_jitter',0) or 0,'p_offset':r.get('p_offset',0) or 0,'gyro_rate_rms':r.get('gyro_rate_rms',0) or 0,'gyro_jitter_rms':r.get('gyro_jitter_rms',0) or 0,'gyro_offset_rms':r.get('gyro_offset_rms',0) or 0})
    return out

def gen_grid(ds,base,wide=True):
    by={}
    for x in ds:by.setdefault(x['true_label'],[]).append(x)
    ad=[x['attention'] for x in by.get('DISTRACTED',[]) if isinstance(x.get('attention'),(int,float))]
    asf=[x['attention'] for x in by.get('STABLE_FOCUS',[]) if isinstance(x.get('attention'),(int,float))]
    unu=[max(x['p_rate'],x['p_jitter'],x['p_offset']) for x in by.get('UNRELIABLE_SIGNAL',[])]
    non=[max(x['p_rate'],x['p_jitter'],x['p_offset']) for x in ds if x['true_label']!='UNRELIABLE_SIGNAL']
    lo=q(ad,[0.1,0.25,0.5,0.75,0.9]) if wide else q(ad,[0.25,0.5,0.75]); hi=q(asf,[0.1,0.25,0.5,0.75,0.9]) if wide else q(asf,[0.25,0.5,0.75])
    st=q(asf,[0.2,0.4,0.6,0.8]); di=q(ad,[0.2,0.4,0.6,0.8])
    mot=sorted(set((q(unu,[0.2,0.4,0.6,0.8])+q(non,[0.6,0.8,0.9])) or [0.5]))
    alpha=sorted(set([max(0.1,min(0.95,base.get('fi_ema_alpha',0.7)+d)) for d in (-0.25,-0.1,0,0.1,0.25)]))
    g={
      'attention_low':sorted(set((lo or [base.get('attention_low_fallback',40)])+[base.get('attention_low_fallback',40)])),
      'attention_high':sorted(set((hi or [base.get('attention_high_fallback',70)])+[base.get('attention_high_fallback',70)])),
      'stable_enter':sorted(set((st or [base.get('stable_enter',60)])+[base.get('stable_enter',60)])),
      'distracted_enter':sorted(set((di or [base.get('distracted_enter',50)])+[base.get('distracted_enter',50)])),
      'fi_ema_alpha':alpha,
      'motion_unreliable_threshold':mot,
      'motion_penalty_weight':[0.05,0.1,0.2,0.3,0.4],
      'motion_score_mode':['max','weighted_sum'],
      'rate_weight':[0.8,1.0,1.2],'jitter_weight':[0.8,1.0,1.2],'offset_weight':[0.8,1.0,1.2],
      'state_hold_strategy':['none','previous_state_hysteresis','neutral_band_keep_previous'],
      'min_state_duration_frames':[1,2,3],'stable_enter_count':[1,2,3],'distracted_enter_count':[1,2,3],
      'ema_warmup_strategy':['reset_per_session','carry_within_session_only','first_frame_raw']
    }
    return g

def predict(ds,p):
    out=[];ctx={}
    for r in sorted(ds,key=lambda x:(x['session_id'],x['start_ms'])):
        sid=r['session_id']; c=ctx.setdefault(sid,{'fi':None,'state':'DISTRACTED','stable_count':0,'dist_count':0,'dur':0})
        if p['motion_score_mode']=='weighted_sum': motion=min(1.0,max(0.0,r['p_rate']*p['rate_weight']+r['p_jitter']*p['jitter_weight']+r['p_offset']*p['offset_weight']))
        else: motion=max(r['p_rate']*p['rate_weight'],r['p_jitter']*p['jitter_weight'],r['p_offset']*p['offset_weight'])
        if (r.get('attention') is None) or (not r.get('attention_fresh')) or (not r.get('gyro_fresh')) or motion>=p['motion_unreliable_threshold']:
            pred='UNRELIABLE_SIGNAL';fi_raw=fi_sm=0;reason='reliability_gate';c['dur']=0
        else:
            att=max(0,min(1,(float(r['attention'])-p['attention_low'])/max(p['attention_high']-p['attention_low'],1e-6)))*100
            fi_raw=0.85*att + p['motion_penalty_weight']*(100*(1-max(0,min(1,motion))))
            if c['fi'] is None or p['ema_warmup_strategy']=='first_frame_raw': c['fi']=fi_raw
            fi_sm=p['fi_ema_alpha']*fi_raw + (1-p['fi_ema_alpha'])*(c['fi'] if c['fi'] is not None else fi_raw); c['fi']=fi_sm
            c['stable_count']=c['stable_count']+1 if fi_sm>=p['stable_enter'] else 0
            c['dist_count']=c['dist_count']+1 if fi_sm<=p['distracted_enter'] else 0
            if c['stable_count']>=p['stable_enter_count']: pred='STABLE_FOCUS'
            elif c['dist_count']>=p['distracted_enter_count']: pred='DISTRACTED'
            else:
                pred='STABLE_FOCUS' if fi_sm>=((p['stable_enter']+p['distracted_enter'])/2) else 'DISTRACTED'
                if p['state_hold_strategy']!='none' and c['dur']<p['min_state_duration_frames']: pred=c['state']
            reason='fi_path'; c['dur']=c['dur']+1 if pred==c['state'] else 1; c['state']=pred
        out.append({**r,'predicted_label':pred,'motion_score':motion,'fi_raw':fi_raw,'fi_smoothed':fi_sm,'reason':reason})
    return out

def metrics(preds):
    labels=sorted(set([x['true_label'] for x in preds]+[x['predicted_label'] for x in preds])); cm={}; total=len(preds);corr=0;pd={};ld={}
    for x in preds:
        t,p=x['true_label'],x['predicted_label']; corr+=int(t==p);ld[t]=ld.get(t,0)+1;pd[p]=pd.get(p,0)+1;cm.setdefault(t,{}).setdefault(p,0);cm[t][p]+=1
    f1=[]
    for c in labels:
        tp=cm.get(c,{}).get(c,0);fp=sum(cm.get(o,{}).get(c,0) for o in labels if o!=c);fn=sum(v for k,v in cm.get(c,{}).items() if k!=c);pr=tp/max(tp+fp,1);rc=tp/max(tp+fn,1);f1.append(0 if pr+rc==0 else 2*pr*rc/(pr+rc))
    macro=sum(f1)/max(len(f1),1);acc=corr/max(total,1)
    um=sum(1 for x in preds if x['true_label']=='UNRELIABLE_SIGNAL' and x['predicted_label']!='UNRELIABLE_SIGNAL'); fu=sum(1 for x in preds if x['true_label']!='UNRELIABLE_SIGNAL' and x['predicted_label']=='UNRELIABLE_SIGNAL')
    fh=sum(1 for x in preds if x['predicted_label']=='HIGH_FOCUS' and x['true_label']!='HIGH_FOCUS'); collapse=max((v/max(total,1) for v in pd.values()),default=0); cp=max(collapse-0.85,0)
    return {'frame_accuracy':acc,'macro_f1':macro,'weighted_f1':sum((ld.get(c,0)/max(total,1))*f1[i] for i,c in enumerate(labels)),'unreliable_miss':um,'unreliable_miss_rate':um/max(total,1),'false_unreliable':fu,'false_unreliable_rate':fu/max(total,1),'false_high_focus':fh,'false_high_focus_rate':fh/max(total,1),'false_fatigue':0,'transition_jitter':0.0,'single_class_collapse_penalty':cp,'prediction_distribution':pd,'label_distribution':ld,'confusion_matrix':cm}

def score(m,worst,mean_cv,trans_pen):
    s=1.0*m['macro_f1']+0.5*m['frame_accuracy']-4*m['unreliable_miss_rate']-2*m['false_unreliable_rate']-2*m['false_high_focus_rate']-0.5*m['transition_jitter']-0.5*m['single_class_collapse_penalty']+0.3*worst+0.2*mean_cv-0.5*trans_pen
    return s,{'macro_f1':1.0*m['macro_f1'],'frame_accuracy':0.5*m['frame_accuracy'],'unreliable_miss_rate':-4*m['unreliable_miss_rate'],'false_unreliable_rate':-2*m['false_unreliable_rate'],'false_high_focus_rate':-2*m['false_high_focus_rate'],'transition_jitter':-0.5*m['transition_jitter'],'single_class_collapse_penalty':-0.5*m['single_class_collapse_penalty'],'worst_session_score':0.3*worst,'mean_validation_score':0.2*mean_cv,'transition_session_penalty':-0.5*trans_pen}

def eval_candidate(args):
    ds,p,sessions,cv_mode=args
    preds=predict(ds,p);m=metrics(preds)
    per=[]
    for s in sessions:
        fm=metrics([x for x in preds if x['session_id']==s]); per.append({'session_id':s,'score':0,'macro_f1':fm['macro_f1'],'frame_accuracy':fm['frame_accuracy'],'unreliable_miss':fm['unreliable_miss'],'false_unreliable':fm['false_unreliable'],'confusion_matrix':fm['confusion_matrix']})
    worst=min((x['macro_f1'] for x in per),default=0); mean_cv=statistics.mean((x['macro_f1'] for x in per)) if per else m['macro_f1']
    trans=[x for x in per if 'distracted_to_focus' in str(x['session_id'])]; trans_pen=max(0,0.4-(statistics.mean([x['macro_f1'] for x in trans]) if trans else mean_cv))
    sc,contrib=score(m,worst,mean_cv,trans_pen)
    for x in per:x['score']=x['macro_f1']
    return {'params':p,'preds':preds,'metrics':{**m,'score':sc,'score_contributions':contrib,'worst_session_score':worst,'mean_validation_score':mean_cv,'transition_session_penalty':trans_pen},'per_session':per}

def main():
    ap=argparse.ArgumentParser();
    ap.add_argument('--input',required=True);ap.add_argument('--labels',required=True);ap.add_argument('--base-config',required=True);ap.add_argument('--out-config',required=True);ap.add_argument('--report',required=True);ap.add_argument('--misclassified-out',required=True);ap.add_argument('--top-k',type=int,default=20);ap.add_argument('--cv-mode',choices=['none','leave-one-session-out'],default='leave-one-session-out');ap.add_argument('--max-combinations',type=int,default=200000);ap.add_argument('--grid-source',choices=['auto','config','both'],default='auto');ap.add_argument('--prediction-mode',choices=['recompute'],default='recompute');ap.add_argument('--search-mode',choices=['grid','coarse-to-fine'],default='coarse-to-fine');ap.add_argument('--stage1-top-k',type=int,default=100);ap.add_argument('--stage2-neighborhood',type=int,default=2);ap.add_argument('--n-jobs',type=int,default=1);ap.add_argument('--rank-by',choices=['balanced','full_score','mean_cv','worst_session','macro_f1'],default='balanced');ap.add_argument('--min-worst-session-score',type=float,default=0.4);ap.add_argument('--min-transition-session-score',type=float,default=0.4);ap.add_argument('--max-false-unreliable-rate',type=float,default=0.15);ap.add_argument('--allow-accepted-with-warnings',action='store_true');ap.add_argument('--device',choices=['cpu','gpu'],default='cpu')
    a=ap.parse_args();t0=time.time();warnings=[]
    if a.device=='gpu':warnings.append('gpu is not implemented; fallback to cpu')
    rows=_load_jsonl(sorted(glob.glob(a.input))); labels,_=_load_labels(sorted(glob.glob(a.labels))); base=load_structured_file(a.base_config); ds=build_ds(rows,labels); sessions=sorted({x['session_id'] for x in ds})
    grid=gen_grid(ds,base,wide=True); keys=list(grid); combos=[dict(zip(keys,c)) for c in itertools.product(*[grid[k] for k in keys])]
    total_gen=len(combos)
    if len(combos)>a.max_combinations: warnings.append('max_combinations truncated search'); combos=combos[:a.max_combinations]
    if a.search_mode=='coarse-to-fine':
        stage1=combos
        jobs=[(ds,p,sessions,a.cv_mode) for p in stage1]
        res1=(mp.Pool(a.n_jobs).map(eval_candidate,jobs) if a.n_jobs>1 else [eval_candidate(j) for j in jobs])
        res1=sorted(res1,key=lambda r:r['metrics']['score'],reverse=True)
        anchors=[r['params'] for r in res1[:a.stage1_top_k]]
        refine=[]
        for p in anchors:
            for d in range(-a.stage2_neighborhood,a.stage2_neighborhood+1):
                q=dict(p); q['attention_low']=p['attention_low']+d; q['attention_high']=p['attention_high']+d; q['stable_enter']=p['stable_enter']+d; q['distracted_enter']=p['distracted_enter']+d; q['fi_ema_alpha']=max(0.1,min(0.95,p['fi_ema_alpha']+d*0.02)); q['motion_unreliable_threshold']=max(0,min(2,p['motion_unreliable_threshold']+d*0.02)); refine.append(q)
        combos2=[dict(t) for t in {tuple(sorted(x.items())) for x in refine}]
        jobs=[(ds,p,sessions,a.cv_mode) for p in combos2]
        res2=(mp.Pool(a.n_jobs).map(eval_candidate,jobs) if a.n_jobs>1 else [eval_candidate(j) for j in jobs])
        results=res1+res2
    else:
        jobs=[(ds,p,sessions,a.cv_mode) for p in combos]
        results=(mp.Pool(a.n_jobs).map(eval_candidate,jobs) if a.n_jobs>1 else [eval_candidate(j) for j in jobs])
    base_p={'attention_low':base.get('attention_low_fallback',40),'attention_high':base.get('attention_high_fallback',70),'stable_enter':base.get('stable_enter',60),'distracted_enter':base.get('distracted_enter',50),'fi_ema_alpha':base.get('fi_ema_alpha',0.7),'motion_unreliable_threshold':0.8,'motion_penalty_weight':0.2,'motion_score_mode':'max','rate_weight':1.0,'jitter_weight':1.0,'offset_weight':1.0,'state_hold_strategy':'none','min_state_duration_frames':1,'stable_enter_count':1,'distracted_enter_count':1,'ema_warmup_strategy':'first_frame_raw'}
    base_r=eval_candidate((ds,base_p,sessions,a.cv_mode))
    base_map={(x['session_id'],x['frame_id'],x['start_ms']):x['predicted_label'] for x in base_r['preds']}
    for r in results:
        m={(x['session_id'],x['frame_id'],x['start_ms']):x['predicted_label'] for x in r['preds']}
        r['changed_prediction_count']=sum(1 for k in set(base_map)|set(m) if base_map.get(k)!=m.get(k))
    if results and all(r['changed_prediction_count']==0 for r in results):warnings.append('candidate config has no effect on predictions; check config propagation or evaluation path.')
    key={'balanced':lambda r:r['metrics']['score'],'full_score':lambda r:r['metrics']['score'],'mean_cv':lambda r:r['metrics']['mean_validation_score'],'worst_session':lambda r:r['metrics']['worst_session_score'],'macro_f1':lambda r:r['metrics']['macro_f1']}[a.rank_by]
    results=sorted(results,key=key,reverse=True); top=results[:a.top_k]; best=top[0] if top else base_r
    # CV folds
    folds=[]
    for hs in sessions:
        cand=sorted(results,key=lambda r: statistics.mean([x['score'] for x in r['per_session'] if x['session_id']!=hs] or [r['metrics']['score']]),reverse=True)[0]
        held=[x for x in cand['per_session'] if x['session_id']==hs][0]
        folds.append({'heldout_session_id':hs,'selected_params':cand['params'],'selection_score':statistics.mean([x['score'] for x in cand['per_session'] if x['session_id']!=hs] or [cand['metrics']['score']]),'heldout_score':held['score'],'heldout_macro_f1':held['macro_f1'],'heldout_unreliable_miss':held['unreliable_miss'],'heldout_false_unreliable':held['false_unreliable'],'heldout_confusion_matrix':held['confusion_matrix']})
    # acceptance checks
    trans_scores=[x['score'] for x in best['per_session'] if 'distracted_to_focus' in str(x['session_id'])]
    transition_score=min(trans_scores) if trans_scores else best['metrics']['worst_session_score']
    checks={
      'score_improved':best['metrics']['score']>base_r['metrics']['score'],'macro_f1_improved':best['metrics']['macro_f1']>=base_r['metrics']['macro_f1'],'accuracy_improved':best['metrics']['frame_accuracy']>=base_r['metrics']['frame_accuracy'],'unreliable_miss_not_worse':best['metrics']['unreliable_miss']<=base_r['metrics']['unreliable_miss'],'false_high_focus_not_worse':best['metrics']['false_high_focus']<=base_r['metrics']['false_high_focus'],'no_single_class_collapse':best['metrics']['single_class_collapse_penalty']==0,'false_unreliable_within_limit':best['metrics']['false_unreliable_rate']<=a.max_false_unreliable_rate,'worst_session_above_threshold':best['metrics']['worst_session_score']>=a.min_worst_session_score,'transition_session_above_threshold':transition_score>=a.min_transition_session_score
    }
    reject=[k for k,v in checks.items() if not v]
    accepted=(all(checks.values()) or (a.allow_accepted_with_warnings and checks['score_improved'] and checks['unreliable_miss_not_worse']))
    if not accepted and not reject: reject=['accepted policy failed with unspecified condition']
    weak=[{'session_id':x['session_id'],'score':x['score'],'macro_f1':x['macro_f1'],'main_error_type':'low_macro_f1','suggested_next_grid_focus':'state_hold_strategy/fi_ema_alpha'} for x in best['per_session'] if x['score']<a.min_worst_session_score]
    if weak:warnings.append('weak sessions detected')
    mis=[x for x in best['preds'] if x['true_label']!=x['predicted_label']]
    with open(a.misclassified_out,'w',encoding='utf-8',newline='') as f:
        cols=['session_id','frame_id','start_ms','end_ms','true_label','predicted_label','attention','motion_score','fi_raw','fi_smoothed','p_rate','p_jitter','p_offset','gyro_rate_rms','gyro_jitter_rms','gyro_offset_rms','reason'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader();[w.writerow({k:r.get(k,'') for k in cols}) for r in mis]
    cfg={'base_config_path':a.base_config,'generated_at':datetime.datetime.utcnow().isoformat()+'Z','calibration_method':'deterministic_grid_search','prediction_mode':'recompute','dataset_meta':{'total_labeled_frames':len(ds),'session_count':len(sessions)},'selected_params':best['params'],'score_summary':{'base_score':base_r['metrics']['score'],'best_score':best['metrics']['score']},'active_grid':grid,'accepted':accepted,'experimental':(not accepted),'reject_reasons':reject,'warnings':warnings}
    Path(a.out_config).write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
    trade={'best_overall_candidate':top[0]['params'] if top else {},'best_worst_session_candidate':max(results,key=lambda r:r['metrics']['worst_session_score'])['params'] if results else {},'best_transition_candidate':max(results,key=lambda r:min([x['score'] for x in r['per_session'] if 'distracted_to_focus' in str(x['session_id'])] or [-1]))['params'] if results else {},'safest_unreliable_candidate':min(results,key=lambda r:r['metrics']['unreliable_miss'])['params'] if results else {},'lowest_false_unreliable_candidate':min(results,key=lambda r:r['metrics']['false_unreliable'])['params'] if results else {}}
    report={'dataset_meta':{'input_files_count':len(sorted(glob.glob(a.input))),'label_files_count':len(sorted(glob.glob(a.labels))),'matched_session_ids':sessions,'session_count':len(sessions),'total_labeled_frames':len(ds),'label_distribution':base_r['metrics']['label_distribution']},'feature_distribution_summary':{'label_distribution':base_r['metrics']['label_distribution']},'active_grid':grid,'grid_generation_summary':{'grid_source':a.grid_source,'search_mode':a.search_mode},'search_summary':{'total_combinations_generated':total_gen,'total_combinations_evaluated':len(results),'max_combinations':a.max_combinations,'skipped_combinations':max(0,total_gen-len(results)),'elapsed_sec':time.time()-t0,'prediction_changed_vs_base':sum(1 for r in results if r['changed_prediction_count']>0),'best_score':best['metrics']['score'],'accepted':accepted,'n_jobs':a.n_jobs},'base_result':base_r['metrics'],'best_result':{**best['metrics'],'params':best['params'],'per_session_scores':best['per_session']},'top_candidates':[{'rank':i+1,'params':r['params'],'score':r['metrics']['score'],'macro_f1':r['metrics']['macro_f1'],'frame_accuracy':r['metrics']['frame_accuracy'],'unreliable_miss':r['metrics']['unreliable_miss'],'false_unreliable':r['metrics']['false_unreliable'],'prediction_distribution':r['metrics']['prediction_distribution'],'worst_session_score':r['metrics']['worst_session_score'],'mean_validation_score':r['metrics']['mean_validation_score']} for i,r in enumerate(top)],'pareto_candidates':[{'params':r['params'],'score':r['metrics']['score']} for r in top[:5]],'safe_candidates':[{'params':r['params'],'unreliable_miss':r['metrics']['unreliable_miss']} for r in sorted(results,key=lambda x:x['metrics']['unreliable_miss'])[:5]],'balanced_candidates':[{'params':r['params'],'score':r['metrics']['score']} for r in top[:5]],'per_session_results':best['per_session'],'cross_validation_results':{'mode':a.cv_mode,'folds':folds,'mean_heldout_score':statistics.mean([f['heldout_score'] for f in folds]) if folds else 0,'worst_heldout_score':min([f['heldout_score'] for f in folds]) if folds else 0,'heldout_by_session':{f['heldout_session_id']:f['heldout_score'] for f in folds},'cv_warnings':[]},'transition_session_diagnosis':{'transition_sessions':[x for x in sessions if 'distracted_to_focus' in str(x)],'transition_score':transition_score,'penalty':best['metrics']['transition_session_penalty']},'acceptance_checks':checks,'reject_reasons':reject,'weak_sessions':weak,'tradeoff_analysis':trade,'warnings':warnings,'score_formula':'...v2 balanced formula'}
    Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'accepted':accepted,'reject_reasons':reject,'best_score':best['metrics']['score']},ensure_ascii=False))

if __name__=='__main__':main()
