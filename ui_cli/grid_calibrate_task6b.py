from __future__ import annotations
import argparse, csv, glob, itertools, json, statistics, time, datetime
from pathlib import Path
from ui_cli.evaluate_task6b import _load_jsonl, _load_labels, load_structured_file


def _quantiles(vals, qs):
    vals=sorted(v for v in vals if isinstance(v,(int,float)))
    if not vals: return []
    out=[]
    for q in qs:
        i=min(len(vals)-1,max(0,int(round((len(vals)-1)*q))))
        out.append(vals[i])
    return sorted(set(out))

def _build_frame_dataset(rows, labels):
    by_s={}
    for r in rows: by_s.setdefault(r.get('session_id'),[]).append(r)
    ds=[]
    for fr in labels:
        if fr.get('label')=='IGNORE': continue
        sid=fr.get('session_id'); a=int(fr.get('start_ms',0)); b=int(fr.get('end_ms',0))
        ev=[r for r in by_s.get(sid,[]) if a<=int(r.get('now_ms',0))<b]
        if not ev: continue
        last=ev[-1]
        ds.append({'session_id':sid,'frame_id':fr.get('frame_id',''),'start_ms':a,'end_ms':b,'true_label':fr.get('label'),'attention':last.get('attention'),'attention_age_ms':last.get('attention_age_ms'),'attention_fresh':last.get('attention_fresh'),'gyro_fresh':last.get('gyro_fresh'),'warning_flags':last.get('warning_flags',[]),'error_flags':last.get('error_flags',[]),'p_rate':last.get('p_rate',0) or 0,'p_jitter':last.get('p_jitter',0) or 0,'p_offset':last.get('p_offset',0) or 0,'gyro_rate_rms':last.get('gyro_rate_rms',0) or 0,'gyro_jitter_rms':last.get('gyro_jitter_rms',0) or 0,'gyro_offset_rms':last.get('gyro_offset_rms',0) or 0})
    return ds

def _gen_grid(ds, base):
    by_lbl={}
    for x in ds: by_lbl.setdefault(x['true_label'],[]).append(x)
    att_d=[x.get('attention') for x in by_lbl.get('DISTRACTED',[]) if isinstance(x.get('attention'),(int,float))]
    att_s=[x.get('attention') for x in by_lbl.get('STABLE_FOCUS',[]) if isinstance(x.get('attention'),(int,float))]
    unr=by_lbl.get('UNRELIABLE_SIGNAL',[]); non=[x for x in ds if x['true_label']!='UNRELIABLE_SIGNAL']
    m_unr=[max(x.get('p_rate',0),x.get('p_jitter',0),x.get('p_offset',0)) for x in unr]
    m_non=[max(x.get('p_rate',0),x.get('p_jitter',0),x.get('p_offset',0)) for x in non]
    low=_quantiles(att_d,[0.25,0.5,0.75]) or [base.get('attention_low_fallback',40)]
    high=_quantiles(att_s,[0.25,0.5,0.75]) or [base.get('attention_high_fallback',70)]
    s_enter=_quantiles(att_s,[0.4,0.6]) or [base.get('stable_enter',60)]
    d_enter=_quantiles(att_d,[0.4,0.6]) or [base.get('distracted_enter',50)]
    mot=sorted(set((_quantiles(m_unr,[0.4,0.6])+_quantiles(m_non,[0.7,0.9])) or [0.5]))
    alpha=sorted(set([max(0.1,min(0.95,base.get('fi_ema_alpha',0.7)+d)) for d in (-0.15,0,0.15)]))
    grid={'attention_low':low+[base.get('attention_low_fallback',40)],'attention_high':high+[base.get('attention_high_fallback',70)],'stable_enter':s_enter+[base.get('stable_enter',60)],'distracted_enter':d_enter+[base.get('distracted_enter',50)],'fi_ema_alpha':alpha,'motion_unreliable_threshold':mot,'motion_penalty_weight':[0.1,0.2,0.3]}
    return {k:sorted(set(v)) for k,v in grid.items()}

def _predict(ds, p):
    out=[]; prev={}
    for r in sorted(ds,key=lambda x:(x['session_id'],x['start_ms'])):
        att=r.get('attention'); mf=bool(r.get('attention_fresh')); gf=bool(r.get('gyro_fresh'))
        motion=max(float(r.get('p_rate',0)),float(r.get('p_jitter',0)),float(r.get('p_offset',0)))
        if (att is None) or (not mf) or (not gf) or motion>=p['motion_unreliable_threshold']:
            pred='UNRELIABLE_SIGNAL'; reason='reliability_gate'
            fi_raw=fi_sm=0.0
        else:
            att_n=max(0,min(1,(float(att)-p['attention_low'])/max(p['attention_high']-p['attention_low'],1e-6)))*100
            s_motion=100*(1-max(0,min(1,motion)))
            fi_raw=0.8*att_n + p['motion_penalty_weight']*s_motion
            ps=prev.get(r['session_id'],fi_raw)
            fi_sm=p['fi_ema_alpha']*fi_raw+(1-p['fi_ema_alpha'])*ps
            prev[r['session_id']]=fi_sm
            if fi_sm<=p['distracted_enter']: pred='DISTRACTED'
            elif fi_sm>=p['stable_enter']: pred='STABLE_FOCUS'
            else: pred='STABLE_FOCUS' if ps>=p['stable_enter'] else 'DISTRACTED'
            reason='fi_path'
        out.append({**r,'predicted_label':pred,'motion_score':motion,'fi_raw':fi_raw,'fi_smoothed':fi_sm,'reason':reason})
    return out

def _metrics(preds):
    labels=sorted(set([x['true_label'] for x in preds]+[x['predicted_label'] for x in preds]))
    cm={}; total=len(preds); correct=sum(1 for x in preds if x['true_label']==x['predicted_label'])
    pd={}; ld={}
    for x in preds:
        t,p=x['true_label'],x['predicted_label']; ld[t]=ld.get(t,0)+1; pd[p]=pd.get(p,0)+1
        cm.setdefault(t,{}).setdefault(p,0); cm[t][p]+=1
    per_f1=[]
    for c in labels:
        tp=cm.get(c,{}).get(c,0); fp=sum(cm.get(o,{}).get(c,0) for o in labels if o!=c); fn=sum(v for k,v in cm.get(c,{}).items() if k!=c)
        pr=tp/max(tp+fp,1); rc=tp/max(tp+fn,1); per_f1.append(0 if pr+rc==0 else 2*pr*rc/(pr+rc))
    macro=sum(per_f1)/max(len(per_f1),1); weighted=sum((ld.get(c,0)/max(total,1))*per_f1[i] for i,c in enumerate(labels))
    un_miss=sum(1 for x in preds if x['true_label']=='UNRELIABLE_SIGNAL' and x['predicted_label']!='UNRELIABLE_SIGNAL')
    false_un=sum(1 for x in preds if x['true_label']!='UNRELIABLE_SIGNAL' and x['predicted_label']=='UNRELIABLE_SIGNAL')
    false_high=sum(1 for x in preds if x['predicted_label']=='HIGH_FOCUS' and x['true_label']!='HIGH_FOCUS')
    false_fat=sum(1 for x in preds if x['predicted_label']=='FATIGUED' and x['true_label']!='FATIGUED')
    collapse=max((v/max(total,1) for v in pd.values()),default=0); collapse_pen=max(collapse-0.85,0)
    score=1.0*macro+0.5*(correct/max(total,1))-4.0*(un_miss/max(total,1))-2.0*(false_un/max(total,1))-2.0*(false_high/max(total,1))-0.5*0.0-0.5*collapse_pen
    return {'score':score,'frame_accuracy':correct/max(total,1),'macro_f1':macro,'weighted_f1':weighted,'unreliable_miss':un_miss,'unreliable_miss_rate':un_miss/max(total,1),'false_unreliable':false_un,'false_unreliable_rate':false_un/max(total,1),'false_high_focus':false_high,'false_fatigue':false_fat,'transition_jitter':0.0,'single_class_collapse_penalty':collapse_pen,'prediction_distribution':pd,'label_distribution':ld,'confusion_matrix':cm,'score_contributions':{'macro_f1':1.0*macro,'frame_accuracy':0.5*(correct/max(total,1)),'unreliable_miss_rate':-4.0*(un_miss/max(total,1)),'false_unreliable_rate':-2.0*(false_un/max(total,1)),'false_high_focus_rate':-2.0*(false_high/max(total,1)),'transition_jitter':0.0,'single_class_collapse_penalty':-0.5*collapse_pen}}

def main():
    ap=argparse.ArgumentParser();
    ap.add_argument('--input',required=True);ap.add_argument('--labels',required=True);ap.add_argument('--base-config',required=True)
    ap.add_argument('--out-config',required=True);ap.add_argument('--report',required=True);ap.add_argument('--misclassified-out',required=True)
    ap.add_argument('--top-k',type=int,default=20);ap.add_argument('--cv-mode',choices=['none','leave-one-session-out'],default='leave-one-session-out')
    ap.add_argument('--max-combinations',type=int,default=20000);ap.add_argument('--grid-source',choices=['auto','config','both'],default='auto')
    ap.add_argument('--prediction-mode',choices=['recompute'],default='recompute')
    a=ap.parse_args(); t0=time.time()
    rows=_load_jsonl(sorted(glob.glob(a.input))); labels,_=_load_labels(sorted(glob.glob(a.labels))); base=load_structured_file(a.base_config)
    ds=_build_frame_dataset(rows,labels); sessions=sorted({x['session_id'] for x in ds});
    grid=_gen_grid(ds,base)
    keys=list(grid); combos=list(itertools.product(*[grid[k] for k in keys]))
    total_gen=len(combos); combos=combos[:a.max_combinations]
    results=[]; warnings=[]
    base_preds=_predict(ds,{**base,'attention_low':base.get('attention_low_fallback',40),'attention_high':base.get('attention_high_fallback',70),'motion_unreliable_threshold':0.8,'motion_penalty_weight':0.2,'stable_enter':base.get('stable_enter',60),'distracted_enter':base.get('distracted_enter',50),'fi_ema_alpha':base.get('fi_ema_alpha',0.7)})
    base_m=_metrics(base_preds)
    base_map={(x['session_id'],x['frame_id'],x['start_ms']):x['predicted_label'] for x in base_preds}
    for c in combos:
        p=dict(zip(keys,c)); preds=_predict(ds,p); m=_metrics(preds)
        cur={(x['session_id'],x['frame_id'],x['start_ms']):x['predicted_label'] for x in preds}
        changed=sum(1 for k in set(base_map)|set(cur) if base_map.get(k)!=cur.get(k))
        cv=[]
        if a.cv_mode=='leave-one-session-out':
            for s in sessions:
                fold=[x for x in preds if x['session_id']==s]; fm=_metrics(fold); cv.append({'session_id':s,'score':fm['score'],'macro_f1':fm['macro_f1'],'unreliable_miss_rate':fm['unreliable_miss_rate']})
        m['mean_validation_score']=statistics.mean([x['score'] for x in cv]) if cv else m['score']
        m['worst_session_score']=min([x['score'] for x in cv]) if cv else m['score']
        results.append({'params':p,'metrics':m,'changed_prediction_count':changed,'per_session_validation':cv,'preds':preds})
    if results and all(r['changed_prediction_count']==0 for r in results): warnings.append('candidate config has no effect on predictions; check config propagation or evaluation path.')
    results=sorted(results,key=lambda r:(r['metrics']['mean_validation_score'],r['metrics']['worst_session_score'],-r['metrics']['unreliable_miss_rate'],r['metrics']['macro_f1']),reverse=True)
    top=results[:a.top_k]; best=top[0] if top else None
    accepted=False
    if best:
        accepted=(best['metrics']['score']>base_m['score'] and best['metrics']['unreliable_miss_rate']<=base_m['unreliable_miss_rate'] and best['metrics']['false_unreliable_rate']<=0.5 and max(best['metrics']['prediction_distribution'].values())/max(sum(best['metrics']['prediction_distribution'].values()),1)<=0.85 and len(ds)>0 and len(sessions)>=2 and best['metrics']['worst_session_score']>=base_m['score']-0.2)
    mis=[x for x in (best['preds'] if best else []) if x['true_label']!=x['predicted_label']]
    cols=['session_id','frame_id','start_ms','end_ms','true_label','predicted_label','attention','motion_score','fi_raw','fi_smoothed','p_rate','p_jitter','p_offset','gyro_rate_rms','gyro_jitter_rms','gyro_offset_rms','reason']
    with open(a.misclassified_out,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();[w.writerow({k:r.get(k,'') for k in cols}) for r in mis]
    cfg={'base_config_path':a.base_config,'generated_at':datetime.datetime.utcnow().isoformat()+'Z','calibration_method':'deterministic_grid_search','prediction_mode':'recompute','dataset_meta':{'total_labeled_frames':len(ds),'session_count':len(sessions)},'selected_params':best['params'] if best else {},'score_summary':{'base_score':base_m['score'],'best_score':best['metrics']['score'] if best else None},'active_grid':grid,'warnings':warnings}
    Path(a.out_config).write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
    fsum={'label_distribution':base_m['label_distribution'],'attention_by_label':{},'p_rate_by_label':{},'p_jitter_by_label':{},'p_offset_by_label':{},'gyro_rate_rms_by_label':{},'gyro_jitter_rms_by_label':{},'gyro_offset_rms_by_label':{}}
    for lbl in fsum['label_distribution']:
        rows_l=[x for x in ds if x['true_label']==lbl]
        for k in ['attention','p_rate','p_jitter','p_offset','gyro_rate_rms','gyro_jitter_rms','gyro_offset_rms']:
            vals=[x.get(k,0) for x in rows_l if isinstance(x.get(k,0),(int,float))]
            tgt={'attention':'attention_by_label','p_rate':'p_rate_by_label','p_jitter':'p_jitter_by_label','p_offset':'p_offset_by_label','gyro_rate_rms':'gyro_rate_rms_by_label','gyro_jitter_rms':'gyro_jitter_rms_by_label','gyro_offset_rms':'gyro_offset_rms_by_label'}[k]
            fsum[tgt][lbl]={'min':min(vals) if vals else None,'max':max(vals) if vals else None,'median':statistics.median(vals) if vals else None}
    report={'dataset_meta':{'input_files_count':len(sorted(glob.glob(a.input))),'label_files_count':len(sorted(glob.glob(a.labels))),'matched_session_ids':sessions,'session_count':len(sessions),'total_labeled_frames':len(ds),'label_distribution':base_m['label_distribution']},'feature_distribution_summary':fsum,'active_grid':grid,'grid_generation_summary':{'grid_source':a.grid_source,'keys':list(grid.keys())},'search_summary':{'total_combinations_generated':total_gen,'total_combinations_evaluated':len(combos),'max_combinations':a.max_combinations,'skipped_combinations':max(total_gen-len(combos),0),'elapsed_sec':time.time()-t0,'prediction_changed_vs_base':sum(1 for r in results if r['changed_prediction_count']>0),'best_score':best['metrics']['score'] if best else None,'accepted':accepted},'base_result':base_m,'best_result':({'params':best['params'],**best['metrics'],'per_session_scores':best['per_session_validation']} if best else {}),'top_candidates':[{'rank':i+1,'params':r['params'],'score':r['metrics']['score'],'macro_f1':r['metrics']['macro_f1'],'frame_accuracy':r['metrics']['frame_accuracy'],'unreliable_miss':r['metrics']['unreliable_miss'],'false_unreliable':r['metrics']['false_unreliable'],'prediction_distribution':r['metrics']['prediction_distribution'],'worst_session_score':r['metrics']['worst_session_score'],'mean_validation_score':r['metrics']['mean_validation_score']} for i,r in enumerate(top)],'per_session_results':best['per_session_validation'] if best else [],'cross_validation_results':{'mode':a.cv_mode,'per_session_validation':best['per_session_validation'] if best else []},'score_formula':'1.0*macro_f1+0.5*accuracy-4.0*unreliable_miss_rate-2.0*false_unreliable_rate-2.0*false_high_focus_rate-0.5*transition_jitter-0.5*single_class_collapse_penalty','warnings':warnings}
    Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'accepted':accepted,'best_score':best['metrics']['score'] if best else None},ensure_ascii=False))

if __name__=='__main__': main()
