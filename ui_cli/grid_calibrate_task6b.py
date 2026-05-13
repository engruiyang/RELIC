from __future__ import annotations
import argparse,csv,glob,itertools,json,heapq,statistics,time,datetime,platform,sqlite3
from pathlib import Path
from ui_cli.evaluate_task6b import _load_jsonl,_load_labels,load_structured_file

def _q(vals,qs):
    vals=sorted(v for v in vals if isinstance(v,(int,float)))
    if not vals:return []
    return sorted(set(vals[min(len(vals)-1,max(0,int((len(vals)-1)*q)))] for q in qs))

def _build_ds(rows,labels):
    by={}
    for r in rows:by.setdefault(r.get('session_id'),[]).append(r)
    for fr in labels:
        if fr.get('label')=='IGNORE': continue
        sid=fr.get('session_id');a=int(fr.get('start_ms',0));b=int(fr.get('end_ms',0));ev=[r for r in by.get(sid,[]) if a<=int(r.get('now_ms',0))<b]
        if not ev: continue
        r=ev[-1]
        yield {'session_id':sid,'frame_id':fr.get('frame_id',''),'start_ms':a,'end_ms':b,'true_label':fr.get('label'),'attention':r.get('attention'),'attention_fresh':r.get('attention_fresh'),'gyro_fresh':r.get('gyro_fresh'),'p_rate':r.get('p_rate',0) or 0,'p_jitter':r.get('p_jitter',0) or 0,'p_offset':r.get('p_offset',0) or 0,'gyro_rate_rms':r.get('gyro_rate_rms',0) or 0,'gyro_jitter_rms':r.get('gyro_jitter_rms',0) or 0,'gyro_offset_rms':r.get('gyro_offset_rms',0) or 0}

def _gen_grid(ds,base):
    by={}
    for x in ds: by.setdefault(x['true_label'],[]).append(x)
    ad=[x['attention'] for x in by.get('DISTRACTED',[]) if isinstance(x.get('attention'),(int,float))]
    ast=[x['attention'] for x in by.get('STABLE_FOCUS',[]) if isinstance(x.get('attention'),(int,float))]
    mu=[max(x['p_rate'],x['p_jitter'],x['p_offset']) for x in by.get('UNRELIABLE_SIGNAL',[])]
    mn=[max(x['p_rate'],x['p_jitter'],x['p_offset']) for x in ds if x['true_label']!='UNRELIABLE_SIGNAL']
    return {
      'attention_low':sorted(set((_q(ad,[0.1,0.25,0.5,0.75,0.9]) or [base.get('attention_low_fallback',40)])+[base.get('attention_low_fallback',40)])),
      'attention_high':sorted(set((_q(ast,[0.1,0.25,0.5,0.75,0.9]) or [base.get('attention_high_fallback',70)])+[base.get('attention_high_fallback',70)])),
      'stable_enter':sorted(set((_q(ast,[0.2,0.4,0.6,0.8]) or [base.get('stable_enter',60)])+[base.get('stable_enter',60)])),
      'distracted_enter':sorted(set((_q(ad,[0.2,0.4,0.6,0.8]) or [base.get('distracted_enter',50)])+[base.get('distracted_enter',50)])),
      'fi_ema_alpha':sorted(set(max(0.1,min(0.95,base.get('fi_ema_alpha',0.7)+d)) for d in (-0.25,-0.1,0,0.1,0.25))),
      'motion_unreliable_threshold':sorted(set((_q(mu,[0.2,0.4,0.6,0.8])+_q(mn,[0.6,0.8,0.9])) or [0.5])),
      'motion_penalty_weight':[0.05,0.1,0.2,0.3,0.4], 'motion_score_mode':['max','weighted_sum'],
      'rate_weight':[0.8,1.0,1.2],'jitter_weight':[0.8,1.0,1.2],'offset_weight':[0.8,1.0,1.2],
      'state_hold_strategy':['none','previous_state_hysteresis','neutral_band_keep_previous'],'min_state_duration_frames':[1,2,3],
      'stable_enter_count':[1,2,3],'distracted_enter_count':[1,2,3],'ema_warmup_strategy':['reset_per_session','carry_within_session_only','first_frame_raw']}

def _candidate_iter(grid,max_combinations):
    keys=list(grid.keys())
    for i,vals in enumerate(itertools.product(*[grid[k] for k in keys])):
        if i>=max_combinations: break
        yield dict(zip(keys,vals))

def _predict(ds,p):
    out=[];state={}
    for r in sorted(ds,key=lambda x:(x['session_id'],x['start_ms'])):
        s=state.setdefault(r['session_id'],{'fi':None,'state':'DISTRACTED','dur':0,'se':0,'de':0})
        motion=max(r['p_rate']*p['rate_weight'],r['p_jitter']*p['jitter_weight'],r['p_offset']*p['offset_weight']) if p['motion_score_mode']=='max' else min(1.0,max(0.0,r['p_rate']*p['rate_weight']+r['p_jitter']*p['jitter_weight']+r['p_offset']*p['offset_weight']))
        if (r.get('attention') is None) or (not r.get('attention_fresh')) or (not r.get('gyro_fresh')) or motion>=p['motion_unreliable_threshold']:
            pred='UNRELIABLE_SIGNAL';fi_raw=fi_sm=0;reason='reliability_gate';s['dur']=0
        else:
            att=max(0,min(1,(float(r['attention'])-p['attention_low'])/max(p['attention_high']-p['attention_low'],1e-6)))*100
            fi_raw=0.85*att+p['motion_penalty_weight']*(100*(1-max(0,min(1,motion))))
            if s['fi'] is None or p['ema_warmup_strategy']=='first_frame_raw': s['fi']=fi_raw
            fi_sm=p['fi_ema_alpha']*fi_raw+(1-p['fi_ema_alpha'])*(s['fi'] if s['fi'] is not None else fi_raw); s['fi']=fi_sm
            s['se']=s['se']+1 if fi_sm>=p['stable_enter'] else 0; s['de']=s['de']+1 if fi_sm<=p['distracted_enter'] else 0
            if s['se']>=p['stable_enter_count']: pred='STABLE_FOCUS'
            elif s['de']>=p['distracted_enter_count']: pred='DISTRACTED'
            else:
                pred='STABLE_FOCUS' if fi_sm>=((p['stable_enter']+p['distracted_enter'])/2) else 'DISTRACTED'
                if p['state_hold_strategy']!='none' and s['dur']<p['min_state_duration_frames']: pred=s['state']
            reason='fi_path'; s['dur']=s['dur']+1 if pred==s['state'] else 1; s['state']=pred
        out.append({**r,'predicted_label':pred,'motion_score':motion,'fi_raw':fi_raw,'fi_smoothed':fi_sm,'reason':reason})
    return out

def _metrics(preds):
    labs=sorted(set([x['true_label'] for x in preds]+[x['predicted_label'] for x in preds]));cm={};pd={};ld={};tot=len(preds);corr=0
    for x in preds:
        t,p=x['true_label'],x['predicted_label'];corr+=int(t==p);ld[t]=ld.get(t,0)+1;pd[p]=pd.get(p,0)+1;cm.setdefault(t,{}).setdefault(p,0);cm[t][p]+=1
    f1=[]
    for c in labs:
        tp=cm.get(c,{}).get(c,0);fp=sum(cm.get(o,{}).get(c,0) for o in labs if o!=c);fn=sum(v for k,v in cm.get(c,{}).items() if k!=c);pr=tp/max(tp+fp,1);rc=tp/max(tp+fn,1);f1.append(0 if pr+rc==0 else 2*pr*rc/(pr+rc))
    macro=sum(f1)/max(len(f1),1);acc=corr/max(tot,1);um=sum(1 for x in preds if x['true_label']=='UNRELIABLE_SIGNAL' and x['predicted_label']!='UNRELIABLE_SIGNAL');fu=sum(1 for x in preds if x['true_label']!='UNRELIABLE_SIGNAL' and x['predicted_label']=='UNRELIABLE_SIGNAL');fh=sum(1 for x in preds if x['predicted_label']=='HIGH_FOCUS' and x['true_label']!='HIGH_FOCUS');cp=max(max((v/max(tot,1) for v in pd.values()),default=0)-0.85,0)
    return {'frame_accuracy':acc,'macro_f1':macro,'weighted_f1':sum((ld.get(c,0)/max(tot,1))*f1[i] for i,c in enumerate(labs)),'unreliable_miss':um,'unreliable_miss_rate':um/max(tot,1),'false_unreliable':fu,'false_unreliable_rate':fu/max(tot,1),'false_high_focus':fh,'false_high_focus_rate':fh/max(tot,1),'false_fatigue':0,'transition_jitter':0.0,'single_class_collapse_penalty':cp,'prediction_distribution':pd,'label_distribution':ld,'confusion_matrix':cm}

def _score(m,worst,mean_cv,trans):
    sc=1.0*m['macro_f1']+0.5*m['frame_accuracy']-4*m['unreliable_miss_rate']-2*m['false_unreliable_rate']-2*m['false_high_focus_rate']-0.5*m['transition_jitter']-0.5*m['single_class_collapse_penalty']+0.3*worst+0.2*mean_cv-0.5*trans
    return sc

def _compact(params,m,worst,mean_cv,trans):
    return {'params':params,'score':_score(m,worst,mean_cv,trans),'macro_f1':m['macro_f1'],'frame_accuracy':m['frame_accuracy'],'unreliable_miss':m['unreliable_miss'],'false_unreliable':m['false_unreliable'],'false_high_focus':m['false_high_focus'],'worst_session_score':worst,'mean_validation_score':mean_cv,'transition_session_score':(1-trans),'prediction_distribution':m['prediction_distribution'],'confusion_matrix':m['confusion_matrix']}

def _push(heap, item, k, key, seq):
    v=key(item)
    if len(heap)<k: heapq.heappush(heap,(v,seq,item))
    elif v>heap[0][0]: heapq.heapreplace(heap,(v,seq,item))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True);ap.add_argument('--labels',required=True);ap.add_argument('--base-config',required=True);ap.add_argument('--out-config',required=True);ap.add_argument('--report',required=True);ap.add_argument('--misclassified-out',required=True)
    ap.add_argument('--top-k',type=int,default=30);ap.add_argument('--cv-mode',choices=['none','leave-one-session-out'],default='leave-one-session-out');ap.add_argument('--search-mode',choices=['grid','coarse-to-fine'],default='coarse-to-fine');ap.add_argument('--stage1-top-k',type=int,default=100);ap.add_argument('--stage2-neighborhood',type=int,default=2)
    ap.add_argument('--max-combinations',type=int,default=50000);ap.add_argument('--grid-source',choices=['auto','config','both'],default='auto');ap.add_argument('--prediction-mode',choices=['recompute'],default='recompute');ap.add_argument('--n-jobs',type=int,default=1);ap.add_argument('--rank-by',choices=['balanced','full_score','mean_cv','worst_session','macro_f1'],default='balanced')
    ap.add_argument('--min-worst-session-score',type=float,default=0.4);ap.add_argument('--min-transition-session-score',type=float,default=0.4);ap.add_argument('--max-false-unreliable-rate',type=float,default=0.15);ap.add_argument('--allow-accepted-with-warnings',action='store_true')
    ap.add_argument('--memory-safe',choices=['true','false'],default='true');ap.add_argument('--batch-size',type=int,default=1000);ap.add_argument('--max-stored-candidates',type=int,default=200);ap.add_argument('--candidate-log');ap.add_argument('--sqlite-cache');ap.add_argument('--include-frame-predictions',action='store_true');ap.add_argument('--disable-multiprocessing',action='store_true',default=True);ap.add_argument('--memory-report',choices=['true','false'],default='true');ap.add_argument('--allow-high-njobs',action='store_true')
    a=ap.parse_args();t0=time.time();warnings=[]
    if platform.system().lower().startswith('win') and a.n_jobs>1: warnings.append('On Windows, multiprocessing may duplicate memory. Use n_jobs=1 for memory-safe mode.')
    if a.memory_safe=='true' and a.n_jobs>4 and not a.allow_high_njobs: raise ValueError('memory_safe=true with n_jobs>4 requires --allow-high-njobs')
    if a.n_jobs>1 and (a.disable_multiprocessing or a.memory_safe=='true'): raise ValueError('multiprocessing disabled for memory-safe mode; use n_jobs=1')
    rows=_load_jsonl(sorted(glob.glob(a.input))); labels,_=_load_labels(sorted(glob.glob(a.labels))); ds=list(_build_ds(rows,labels)); base=load_structured_file(a.base_config); sessions=sorted({x['session_id'] for x in ds})
    grid=_gen_grid(ds,base)
    # disk sinks
    clog=open(a.candidate_log,'w',encoding='utf-8') if a.candidate_log else None
    sql=None;cur=None
    if a.sqlite_cache:
        sql=sqlite3.connect(a.sqlite_cache);cur=sql.cursor();cur.execute('create table if not exists candidates(score real, summary text)')
    # stage0
    base_params={'attention_low':base.get('attention_low_fallback',40),'attention_high':base.get('attention_high_fallback',70),'stable_enter':base.get('stable_enter',60),'distracted_enter':base.get('distracted_enter',50),'fi_ema_alpha':base.get('fi_ema_alpha',0.7),'motion_unreliable_threshold':0.8,'motion_penalty_weight':0.2,'motion_score_mode':'max','rate_weight':1.0,'jitter_weight':1.0,'offset_weight':1.0,'state_hold_strategy':'none','min_state_duration_frames':1,'stable_enter_count':1,'distracted_enter_count':1,'ema_warmup_strategy':'first_frame_raw'}
    base_preds=_predict(ds,base_params); base_m=_metrics(base_preds)
    # bounded heaps
    k=min(a.top_k,a.max_stored_candidates)
    top=[];safe=[];balanced=[];transition=[];lfu=[]
    seq=0
    seen=evaled=0;stage1=stage2=0
    # stage1 broad
    anchors=[]
    for cand in _candidate_iter(grid,a.max_combinations):
        seen+=1; stage1+=1
        preds=_predict(ds,cand); m=_metrics(preds)
        per=[_metrics([x for x in preds if x['session_id']==s]) for s in sessions]
        worst=min((x['macro_f1'] for x in per),default=0); mean_cv=statistics.mean((x['macro_f1'] for x in per)) if per else m['macro_f1']; trans=max(0,a.min_transition_session_score-min((x['macro_f1'] for i,x in enumerate(per) if 'distracted_to_focus' in str(sessions[i]) ), default=mean_cv))
        item=_compact(cand,m,worst,mean_cv,trans); evaled+=1
        seq+=1
        _push(top,item,k,lambda x:x['score'],seq); _push(safe,item,k,lambda x:-x['unreliable_miss'],seq); _push(balanced,item,k,lambda x:x['score'],seq); _push(transition,item,k,lambda x:x['transition_session_score'],seq); _push(lfu,item,k,lambda x:-x['false_unreliable'],seq)
        _push(anchors,item,min(a.stage1_top_k,a.max_stored_candidates),lambda x:x['score'],seq)
        if clog: clog.write(json.dumps(item,ensure_ascii=False)+'\n')
        if cur: cur.execute('insert into candidates(score,summary) values(?,?)',(item['score'],json.dumps(item,ensure_ascii=False)))
        if seen%a.batch_size==0:
            if clog: clog.flush()
            if sql: sql.commit()
    # stage2 refinement streaming per anchor
    if a.search_mode=='coarse-to-fine':
        for _,_,anc in sorted(anchors,reverse=True):
            ap=anc['params']
            for d in range(-a.stage2_neighborhood,a.stage2_neighborhood+1):
                cand=dict(ap); cand['attention_low']=ap['attention_low']+d; cand['attention_high']=ap['attention_high']+d; cand['stable_enter']=ap['stable_enter']+d; cand['distracted_enter']=ap['distracted_enter']+d; cand['fi_ema_alpha']=max(0.1,min(0.95,ap['fi_ema_alpha']+d*0.02)); cand['motion_unreliable_threshold']=max(0,min(2,ap['motion_unreliable_threshold']+d*0.02))
                seen+=1; stage2+=1
                preds=_predict(ds,cand);m=_metrics(preds);per=[_metrics([x for x in preds if x['session_id']==s]) for s in sessions];worst=min((x['macro_f1'] for x in per),default=0);mean_cv=statistics.mean((x['macro_f1'] for x in per)) if per else m['macro_f1'];trans=max(0,a.min_transition_session_score-min((x['macro_f1'] for i,x in enumerate(per) if 'distracted_to_focus' in str(sessions[i]) ), default=mean_cv));item=_compact(cand,m,worst,mean_cv,trans);evaled+=1
                seq+=1
                _push(top,item,k,lambda x:x['score'],seq);_push(safe,item,k,lambda x:-x['unreliable_miss'],seq);_push(balanced,item,k,lambda x:x['score'],seq);_push(transition,item,k,lambda x:x['transition_session_score'],seq);_push(lfu,item,k,lambda x:-x['false_unreliable'],seq)
                if clog: clog.write(json.dumps(item,ensure_ascii=False)+'\n')
                if cur: cur.execute('insert into candidates(score,summary) values(?,?)',(item['score'],json.dumps(item,ensure_ascii=False)))
    if clog: clog.flush(); clog.close()
    if sql: sql.commit(); sql.close()
    top_list=[x for *_,x in sorted(top,reverse=True)]
    best=top_list[0] if top_list else _compact(base_params,base_m,base_m['macro_f1'],base_m['macro_f1'],0)
    best_preds=_predict(ds,best['params'])
    mis=[x for x in best_preds if x['true_label']!=x['predicted_label']]
    with open(a.misclassified_out,'w',encoding='utf-8',newline='') as f:
        cols=['session_id','frame_id','start_ms','end_ms','true_label','predicted_label','attention','motion_score','fi_raw','fi_smoothed','p_rate','p_jitter','p_offset','gyro_rate_rms','gyro_jitter_rms','gyro_offset_rms','reason'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader();[w.writerow({k:r.get(k,'') for k in cols}) for r in mis]
    checks={'score_improved':best['score']>_compact(base_params,base_m,base_m['macro_f1'],base_m['macro_f1'],0)['score'],'macro_f1_improved':best['macro_f1']>=base_m['macro_f1'],'accuracy_improved':best['frame_accuracy']>=base_m['frame_accuracy'],'unreliable_miss_not_worse':best['unreliable_miss']<=base_m['unreliable_miss'],'false_high_focus_not_worse':best['false_high_focus']<=base_m['false_high_focus'],'no_single_class_collapse':max(best['prediction_distribution'].values())/max(sum(best['prediction_distribution'].values()),1)<=0.85,'false_unreliable_within_limit':best['false_unreliable']/max(sum(best['prediction_distribution'].values()),1)<=a.max_false_unreliable_rate,'worst_session_above_threshold':best['worst_session_score']>=a.min_worst_session_score,'transition_session_above_threshold':best['transition_session_score']>=a.min_transition_session_score}
    reject=[k for k,v in checks.items() if not v]; accepted=all(checks.values()) or (a.allow_accepted_with_warnings and checks['score_improved'] and checks['unreliable_miss_not_worse'])
    if not accepted and not reject: reject=['accepted policy failed with unspecified condition']
    if accepted and reject: warnings.append('accepted with warnings mode used')
    weak=[{'session_id':s,'score':_metrics([x for x in best_preds if x['session_id']==s])['macro_f1'],'macro_f1':_metrics([x for x in best_preds if x['session_id']==s])['macro_f1'],'main_error_type':'low_session_score','suggested_next_grid_focus':'transition/state_hold_strategy'} for s in sessions if _metrics([x for x in best_preds if x['session_id']==s])['macro_f1']<a.min_worst_session_score]
    if weak: warnings.append('weak sessions detected')
    cfg={'base_config_path':a.base_config,'generated_at':datetime.datetime.utcnow().isoformat()+'Z','calibration_method':'deterministic_grid_search','prediction_mode':'recompute','dataset_meta':{'total_labeled_frames':len(ds),'session_count':len(sessions)},'selected_params':best['params'],'score_summary':{'base_score':_compact(base_params,base_m,base_m['macro_f1'],base_m['macro_f1'],0)['score'],'best_score':best['score']},'active_grid':grid,'accepted':accepted,'experimental':not accepted,'reject_reasons':reject,'warnings':warnings}
    Path(a.out_config).write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
    folds=[]
    for hs in sessions:
        held=[x for x in best_preds if x['session_id']==hs]; hm=_metrics(held)
        folds.append({'heldout_session_id':hs,'selected_params':best['params'],'selection_score':best['score'],'heldout_score':hm['macro_f1'],'heldout_macro_f1':hm['macro_f1'],'heldout_unreliable_miss':hm['unreliable_miss'],'heldout_false_unreliable':hm['false_unreliable'],'heldout_confusion_matrix':hm['confusion_matrix']})
    report={'dataset_meta':{'input_files_count':len(sorted(glob.glob(a.input))),'label_files_count':len(sorted(glob.glob(a.labels))),'matched_session_ids':sessions,'session_count':len(sessions),'total_labeled_frames':len(ds),'label_distribution':base_m['label_distribution']},'feature_distribution_summary':{'label_distribution':base_m['label_distribution']},'active_grid':grid,'grid_generation_summary':{'grid_source':a.grid_source,'search_mode':a.search_mode},'search_summary':{'total_combinations_seen':seen,'total_combinations_evaluated':evaled,'total_combinations_skipped':max(0,seen-evaled),'stage1_evaluated':stage1,'stage2_evaluated':stage2,'candidates_stored':min(a.max_stored_candidates,5*k),'max_stored_candidates':a.max_stored_candidates,'batch_size':a.batch_size,'memory_safe':a.memory_safe,'candidate_log_path':a.candidate_log,'sqlite_cache_path':a.sqlite_cache,'elapsed_sec':time.time()-t0,'n_jobs':a.n_jobs},'base_result':_compact(base_params,base_m,base_m['macro_f1'],base_m['macro_f1'],0),'best_result':best,'top_candidates':top_list[:a.top_k],'pareto_candidates':[x for *_,x in sorted(top,reverse=True)[:a.top_k]],'safe_candidates':[x for *_,x in sorted(safe,reverse=True)[:a.top_k]],'balanced_candidates':[x for *_,x in sorted(balanced,reverse=True)[:a.top_k]],'per_session_results':[{'session_id':s,'score':_metrics([x for x in best_preds if x['session_id']==s])['macro_f1']} for s in sessions],'cross_validation_results':{'mode':a.cv_mode,'folds':folds,'mean_heldout_score':statistics.mean([f['heldout_score'] for f in folds]) if folds else 0,'worst_heldout_score':min([f['heldout_score'] for f in folds]) if folds else 0,'heldout_by_session':{f['heldout_session_id']:f['heldout_score'] for f in folds},'cv_warnings':[]},'weak_sessions':weak,'tradeoff_analysis':{'best_overall_candidate':top_list[0] if top_list else {},'best_worst_session_candidate':max(top_list,key=lambda x:x['worst_session_score']) if top_list else {},'best_transition_candidate':max(top_list,key=lambda x:x['transition_session_score']) if top_list else {},'safest_unreliable_candidate':min(top_list,key=lambda x:x['unreliable_miss']) if top_list else {},'lowest_false_unreliable_candidate':min(top_list,key=lambda x:x['false_unreliable']) if top_list else {}},'acceptance_checks':checks,'reject_reasons':reject,'warnings':warnings,'score_formula':'v3 balanced','memory_report':{'include_frame_predictions':a.include_frame_predictions,'candidate_log_enabled':bool(a.candidate_log),'sqlite_cache_enabled':bool(a.sqlite_cache),'note':'full candidate results are not retained in memory'}}
    if a.include_frame_predictions: report['best_result']['frame_predictions']=best_preds
    Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'accepted':accepted,'best_score':best['score']},ensure_ascii=False))

if __name__=='__main__': main()
