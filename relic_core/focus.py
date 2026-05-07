from .models import RealtimeSnapshot, GameMetrics, QualityResult, FocusResult
class FocusModel:
    def compute(self,snapshot,metrics=None,quality:QualityResult|None=None):
        s=snapshot if isinstance(snapshot,RealtimeSnapshot) else RealtimeSnapshot.from_dict(snapshot)
        m=metrics if isinstance(metrics,GameMetrics) else GameMetrics(**metrics) if isinstance(metrics,dict) else GameMetrics()
        reasons=[]; valid=True
        if s.attention_value is None: s_eeg=0.5; valid=False; reasons.append('missing_attention')
        else: s_eeg=max(0,min(1,s.attention_value/100))
        penalty=0.5 if (not s.gyro_valid) else min(1.0,(s.gyro_age_ms or 0)/2000)
        s_imu=max(0,min(1,1-penalty))
        if metrics is None: s_b=0.5
        else:
            a=0.5 if m.accuracy is None else m.accuracy; o=0 if m.omission is None else m.omission; f=0 if m.false_action is None else m.false_action; rt=0.5 if m.rt_stability is None else m.rt_stability
            s_b=max(0,min(1,0.35*a+0.20*(1-o)+0.15*(1-f)+0.30*rt))
        fi=100*(0.55*s_eeg+0.15*s_imu+0.30*s_b)
        if quality and quality.status=='error': fi*=0.7; valid=False; reasons.append('low_quality')
        return FocusResult(fi=fi,s_eeg=s_eeg,s_imu=s_imu,s_b=s_b,valid=valid,reasons=reasons)
