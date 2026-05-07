from .models import RealtimeSnapshot, QualityResult
class QualityManager:
    def __init__(self,attention_stale_ms:int=3000,gyro_stale_ms:int=500,attention_zero_warning_ms:int=10000):
        self.attention_stale_ms=attention_stale_ms; self.gyro_stale_ms=gyro_stale_ms; self.attention_zero_warning_ms=attention_zero_warning_ms
    def evaluate(self,snapshot):
        s=snapshot if isinstance(snapshot,RealtimeSnapshot) else RealtimeSnapshot.from_dict(snapshot)
        if not s.connected: return QualityResult(0.0,'error',['disconnected'])
        sqi=1.0; r=[]
        if (not s.attention_valid) or (s.attention_age_ms is not None and s.attention_age_ms>self.attention_stale_ms): sqi-=0.35; r.append('attention_stale_or_invalid')
        if (not s.gyro_valid) or (s.gyro_age_ms is not None and s.gyro_age_ms>self.gyro_stale_ms): sqi-=0.35; r.append('gyro_stale_or_invalid')
        if s.attention_value==0: sqi-=0.1; r.append('attention_zero')
        status='ok' if sqi>=0.8 else ('warning' if sqi>=0.4 else 'error')
        return QualityResult(sqi,status,r)
