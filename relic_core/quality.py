from .models import QualityResult, RealtimeSnapshot

class QualityManager:
    def __init__(self, attention_stale_ms: int = 3000, gyro_stale_ms: int = 500, algorithm_stream_stale_ms: int = 3000,
                 attention_stream_timeout_ms: int = 8000, gyro_stream_timeout_ms: int = 3000, initial_wait_grace_ms: int = 3000, **_: int):
        self.attention_stale_ms=attention_stale_ms; self.gyro_stale_ms=gyro_stale_ms; self.algorithm_stream_stale_ms=algorithm_stream_stale_ms
        self.attention_stream_timeout_ms=attention_stream_timeout_ms; self.gyro_stream_timeout_ms=gyro_stream_timeout_ms; self.initial_wait_grace_ms=initial_wait_grace_ms

    def evaluate(self, snapshot):
        s = snapshot if isinstance(snapshot, RealtimeSnapshot) else RealtimeSnapshot.from_dict(snapshot)
        reasons=[]; sqi=1.0
        if not s.bridge_connected: return QualityResult(0.0,'error',['bridge_disconnected'])
        if not s.bridge_alive: return QualityResult(0.0,'error',['bridge_dead'])

        if s.last_algorithm_msg_age_ms is None:
            if (s.attention_age_ms is None and s.gyro_age_ms is None) or max((s.attention_age_ms or 0),(s.gyro_age_ms or 0))<=self.initial_wait_grace_ms:
                return QualityResult(0.6,'warning',['initial_waiting'])
        else:
            if s.last_algorithm_msg_age_ms>self.algorithm_stream_stale_ms:
                reasons.extend(['algorithm_stream_stale','sensor_stream_inactive'])

        att_stale = s.attention_age_ms is None or s.attention_age_ms>self.attention_stale_ms
        gyro_stale = s.gyro_age_ms is None or s.gyro_age_ms>self.gyro_stale_ms
        if att_stale: reasons.append('attention_stale'); sqi-=0.2
        if gyro_stale: reasons.append('gyro_stale'); sqi-=0.2

        severe_stale = ((s.attention_age_ms is not None and s.attention_age_ms>self.attention_stream_timeout_ms) and
                        (s.gyro_age_ms is not None and s.gyro_age_ms>self.gyro_stream_timeout_ms))
        if severe_stale:
            if 'sensor_stream_inactive' not in reasons: reasons.append('sensor_stream_inactive')
            return QualityResult(0.3,'error',reasons)
        if 'algorithm_stream_stale' in reasons or 'sensor_stream_inactive' in reasons:
            return QualityResult(0.3,'error',reasons)

        if reasons:
            return QualityResult(min(sqi,0.79),'warning',reasons)
        return QualityResult(0.95,'ok',[])
