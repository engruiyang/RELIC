from data.realtime_snapshot import RealtimeSnapshot

class DataCenter:
    def __init__(self, config:dict|None=None):
        self.cfg={
            'attention_fresh_ms':1500,'attention_lost_ms':5000,'gyro_fresh_ms':500,'gyro_lost_ms':2000,
            'focus_fresh_ms':500,'focus_lost_ms':2000,'algorithm_fresh_ms':500,'algorithm_lost_ms':2000,
            'focus_jump_threshold':200.0,'gyro_spike_threshold':80.0,'min_sqi':0.4,
        }
        if config: self.cfg.update(config)
        self._s=RealtimeSnapshot()
        self._last_focus=None; self._last_gyro=None

    def ingest_events(self,events:list[dict],now_ms:int)->None:
        for e in events:
            if e.get('type')=='device_status':
                self._s.device_connected=bool(e.get('device_connected',False)); self._s.bridge_alive=bool(e.get('bridge_alive',False))
            elif e.get('type')=='algorithm_frame':
                self._s.last_algorithm_update_ms=now_ms
                algo=e.get('algorithm'); d=e.get('data',{})
                if algo=='attention' and d.get('attention') is not None:
                    self._s.attention=int(d['attention']); self._s.attention_last_update_ms=now_ms; self._s.attention_seen_once=True
                if algo=='gyroscope':
                    fx,fy=d.get('focus_x'),d.get('focus_y')
                    gx,gy,gz=d.get('gyro_x'),d.get('gyro_y'),d.get('gyro_z')
                    if fx is not None and fy is not None:
                        if self._last_focus is not None and (abs(fx-self._last_focus[0])+abs(fy-self._last_focus[1])>self.cfg['focus_jump_threshold']):
                            self._s.warning_flags.append('focus_jump')
                        self._s.focus_x=fx; self._s.focus_y=fy; self._s.focus_last_update_ms=now_ms; self._s.focus_seen_once=True; self._last_focus=(fx,fy)
                    if None not in (gx,gy,gz):
                        if self._last_gyro is not None and max(abs(gx-self._last_gyro[0]),abs(gy-self._last_gyro[1]),abs(gz-self._last_gyro[2]))>self.cfg['gyro_spike_threshold']:
                            self._s.warning_flags.append('gyro_spike')
                        self._s.gyro_x=gx; self._s.gyro_y=gy; self._s.gyro_z=gz; self._s.gyro_last_update_ms=now_ms; self._s.gyro_seen_once=True; self._last_gyro=(gx,gy,gz)

    def _age(self,now,last): return None if last is None else max(0,now-last)

    def tick(self,now_ms:int)->RealtimeSnapshot:
        s=self._s; s.now_ms=now_ms
        s.warning_flags=[]; s.error_flags=[]
        s.attention_age_ms=self._age(now_ms,s.attention_last_update_ms); s.gyro_age_ms=self._age(now_ms,s.gyro_last_update_ms); s.focus_age_ms=self._age(now_ms,s.focus_last_update_ms); s.last_algorithm_age_ms=self._age(now_ms,s.last_algorithm_update_ms)
        s.attention_fresh=(s.attention_age_ms is not None and s.attention_age_ms<=self.cfg['attention_fresh_ms'])
        s.gyro_fresh=(s.gyro_age_ms is not None and s.gyro_age_ms<=self.cfg['gyro_fresh_ms'])
        s.focus_fresh=(s.focus_age_ms is not None and s.focus_age_ms<=self.cfg['focus_fresh_ms'])

        if not s.attention_seen_once: s.warning_flags.append('attention_missing')
        elif s.attention_age_ms and s.attention_age_ms>self.cfg['attention_lost_ms']: s.error_flags.append('attention_lost')
        elif s.attention_age_ms and s.attention_age_ms>self.cfg['attention_fresh_ms']: s.warning_flags.append('attention_stale')
        if s.gyro_seen_once and s.gyro_age_ms and s.gyro_age_ms>self.cfg['gyro_lost_ms']: s.error_flags.append('gyro_lost')
        elif s.gyro_seen_once and s.gyro_age_ms and s.gyro_age_ms>self.cfg['gyro_fresh_ms']: s.warning_flags.append('gyro_stale')
        if s.focus_seen_once and s.focus_age_ms and s.focus_age_ms>self.cfg['focus_lost_ms']: s.warning_flags.append('focus_lost')
        elif s.focus_seen_once and s.focus_age_ms and s.focus_age_ms>self.cfg['focus_fresh_ms']: s.warning_flags.append('focus_stale')

        s.stream_alive = s.last_algorithm_age_ms is not None and s.last_algorithm_age_ms<=self.cfg['algorithm_lost_ms']
        s.sensor_stream_active = s.last_algorithm_age_ms is not None and s.last_algorithm_age_ms<=self.cfg['algorithm_fresh_ms']
        if not s.device_connected: s.error_flags.append('device_disconnected')
        if not s.stream_alive: s.error_flags.append('stream_inactive')

        sqi=1.0-0.15*len(set(s.warning_flags))-0.35*len(set(s.error_flags)); s.sqi=max(0.0,min(1.0,sqi))
        if s.error_flags: s.quality='error'
        elif s.warning_flags: s.quality='warning'
        else: s.quality='ok'
        s.quality_reasons=list(dict.fromkeys(s.error_flags+s.warning_flags))

        s.fi=float(s.attention or 0)
        ready_core = s.device_connected and s.stream_alive and s.attention_seen_once and (s.attention_age_ms is not None and s.attention_age_ms<=self.cfg['attention_lost_ms']) and (s.gyro_seen_once or s.focus_seen_once) and not s.error_flags and s.sqi>=self.cfg['min_sqi']
        s.training_data_valid=bool(ready_core)
        s.fi_valid=s.training_data_valid
        s.fi_provisional=not s.fi_valid
        if not s.attention_seen_once: s.control_state='WARMUP'
        elif not s.training_data_valid: s.control_state='NO_SIGNAL'
        elif s.fi>=80: s.control_state='HIGH_FOCUS'
        elif s.fi>=60: s.control_state='STABLE_FOCUS'
        elif s.fi>=40: s.control_state='DISTRACTED'
        else: s.control_state='FATIGUED'
        return s

    def get_snapshot(self)->RealtimeSnapshot:
        return self._s
