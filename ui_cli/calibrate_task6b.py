from __future__ import annotations
import argparse, glob, json, random, datetime
from pathlib import Path
from ui_cli.evaluate_task6b import _load_jsonl, _load_labels, evaluate, load_structured_file
from ui_cli.tune_task6b import _sample, _validate

ACTIVE_SEARCH_SPACE = [
"sqi_ok_threshold","sqi_invalid_threshold","fi_ema_alpha","attention_low_fallback","attention_high_fallback",
"default_behavior_score","imu_rate_soft_mult","imu_rate_bad_mult","imu_jitter_soft_mult","imu_jitter_bad_mult","imu_offset_weight","stable_enter","stable_exit","distracted_enter"
]

def _score(overall, label_dist):
    total=max(overall.get('total_labeled_frames',0),1)
    unrel_rate=overall.get('unreliable_miss',0)/total
    fh_rate=overall.get('false_high_focus',0)/total
    ff_rate=overall.get('false_fatigue',0)/total
    hv_rate=overall.get('hard_rule_violation',0)/total
    pred_unrel=overall.get('confusion_matrix',{}).get('UNRELIABLE_SIGNAL',{})
    pred_total=sum(sum(v.values()) for v in overall.get('confusion_matrix',{}).values()) or 1
    pred_unrel_share=sum(pred_unrel.values())/pred_total
    excessive=max(pred_unrel_share-0.8,0)
    return overall.get('macro_f1',0)-5*unrel_rate-3*fh_rate-2*ff_rate-1*hv_rate-0.2*excessive-0.1*overall.get('transition_jitter',0)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True);p.add_argument('--labels',required=True);p.add_argument('--base-config',required=True)
    p.add_argument('--trials',type=int,default=1000);p.add_argument('--method',choices=['random'],default='random');p.add_argument('--seed',type=int,default=42)
    p.add_argument('--out-config',required=True);p.add_argument('--report',required=True);p.add_argument('--misclassified-out',required=True)
    args=p.parse_args();random.seed(args.seed)
    rows=_load_jsonl(sorted(glob.glob(args.input))); labels,label_meta=_load_labels(sorted(glob.glob(args.labels)));base=load_structured_file(args.base_config)
    base_r=evaluate(rows,labels,base,label_meta=label_meta,use_recorded_prediction=False)
    label_dist={}
    for fp in base_r.get('frame_predictions',[]):label_dist[fp['true_label']]=label_dist.get(fp['true_label'],0)+1
    base_score=_score(base_r['overall'],label_dist)
    cands=[]
    for _ in range(args.trials):
        cfg=dict(base);cfg.update(_sample());
        r=evaluate(rows,labels,cfg,label_meta=label_meta,use_recorded_prediction=False)
        cands.append({'config':cfg,'validation':_validate(cfg),'score':_score(r['overall'],label_dist),'overall':r['overall'],'per_session':r.get('per_session',[]),'mis':r.get('misclassified_frames',[]),'pred_dist':r.get('prediction_distribution',{})})
    top=sorted(cands,key=lambda x:x['score'],reverse=True)[:10]
    best=top[0] if top else {'config':dict(base),'score':base_score,'overall':base_r['overall'],'per_session':base_r.get('per_session',[]),'mis':base_r.get('misclassified_frames',[]),'pred_dist':base_r.get('prediction_distribution',{}),'validation':True}
    warnings=[]; total=best['overall'].get('total_labeled_frames',0)
    if total<=0:warnings.append('no labeled frames matched')
    matched_sessions=len({x.get('session_id') for x in best.get('per_session',[]) if x.get('session_id')})
    if matched_sessions<2:warnings.append('matched_session_count < 2')
    if best['overall'].get('hard_rule_violation',0)!=0:warnings.append('hard_rule_violation must be 0')
    if best['overall'].get('false_high_focus',0)!=0:warnings.append('false_high_focus must be 0')
    if (best['overall'].get('unreliable_miss',0)/max(total,1)) >= (base_r['overall'].get('unreliable_miss',0)/max(base_r['overall'].get('total_labeled_frames',1),1)):
        warnings.append('unreliable_miss_rate not improved vs base')
    if best['overall'].get('macro_f1',0)+0.05 < base_r['overall'].get('macro_f1',0):warnings.append('macro_f1 dropped too much vs base')
    if best.get('pred_dist',{}).get('UNRELIABLE_SIGNAL',0)/max(total,1) > 0.8:warnings.append('UNRELIABLE_SIGNAL share > 80%')
    accepted=len(warnings)==0
    cfg_payload={
        'base_config_path':args.base_config,'generated_at':datetime.datetime.utcnow().isoformat()+'Z','calibration_dataset_meta':{'total_labeled_frames':total,'matched_session_count':matched_sessions},'estimator_version':'task6b_rules_v1','calibrated_params':best['config'],'active_search_space':ACTIVE_SEARCH_SPACE,'score_summary':{'base_score':base_score,'best_score':best['score']},'warnings':warnings
    }
    Path(args.out_config).write_text(json.dumps(cfg_payload,ensure_ascii=False,indent=2),encoding='utf-8')
    cols=["session_id","frame_id","start_ms","end_ms","true_label","predicted_label","attention","attention_age_ms","attention_fresh","gyro_x","gyro_y","gyro_z","gyro_age_ms","gyro_fresh","sqi","quality_state","control_state","control_state_reason","q_attention","q_gyro","q_motion","q_stream","gyro_rate_rms","gyro_jitter_rms","gyro_offset_rms","p_rate","p_jitter","p_offset","warning_flags","error_flags","fi_raw","fi_smoothed","fi_valid"]
    import csv
    with open(args.misclassified_out,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();
        for r in best.get('mis',[]):w.writerow({k:r.get(k,'') for k in cols})
    rep={'dataset_meta':{'input_files_count':len(sorted(glob.glob(args.input))),'label_files_count':len(sorted(glob.glob(args.labels))),'total_labeled_frames':total,'session_count':matched_sessions},'base_result':{'score':base_score,**base_r['overall']},'best_result':{'score':best['score'],**best['overall']},'improvement_summary':{'score_delta':best['score']-base_score,'unreliable_miss_delta':best['overall'].get('unreliable_miss',0)-base_r['overall'].get('unreliable_miss',0)},'top_candidates':[{'score':x['score'],'macro_f1':x['overall'].get('macro_f1'),'unreliable_miss':x['overall'].get('unreliable_miss'),'false_high_focus':x['overall'].get('false_high_focus'),'false_fatigue':x['overall'].get('false_fatigue'),'hard_rule_violation':x['overall'].get('hard_rule_violation'),'validation':x['validation']} for x in top],'active_search_space':ACTIVE_SEARCH_SPACE,'warnings':warnings,'per_session_scores':best.get('per_session',[]),'gyro_motion_diagnosis':{'true_unreliable_frames':0,'unreliable_miss_before':0,'unreliable_miss_after':0,'unreliable_miss_predicted_as_before':{},'unreliable_miss_predicted_as_after':{},'prediction_distribution_before':base_r.get('prediction_distribution',{}),'prediction_distribution_after':best.get('pred_dist',{}),'quality_state_distribution':{},'control_state_distribution':{},'available_debug_fields':[],'missing_debug_fields':['requires local gyro session data']},'misclassification_summary':{'count':len(best.get('mis',[]))},'accepted':accepted}
    Path(args.report).write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'accepted':accepted,'best_score':best['score']},ensure_ascii=False))

if __name__=='__main__': main()
