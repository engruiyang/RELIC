from data.realtime_snapshot import RealtimeSnapshot


class DataCenter:
<<<<<<< codex/fix-datacenter-and-cli-debug-outputs-xjefpe
    def __init__(self, config: dict | None = None):
        self.cfg = {
            'attention_fresh_ms': 1500,
            'attention_lost_ms': 5000,
            'gyro_fresh_ms': 500,
            'gyro_lost_ms': 2000,
            'focus_fresh_ms': 500,
            'focus_lost_ms': 2000,
            'algorithm_fresh_ms': 500,
            'algorithm_lost_ms': 2000,
            'focus_jump_threshold': 200.0,
            'gyro_spike_threshold': 80.0,
            'min_sqi': 0.45,
            'warning_sqi': 0.8,
            'error_sqi': 0.4,
            'fatigued_enter_ms': 9000,
            'fatigued_exit_ms': 3000,
            'stable_enter_ticks': 3,
            'stable_exit_threshold': 55,
            'stable_enter_threshold': 60,
            'warning_allows_fi_valid': False,
            'allow_stale_attention_fi_valid': False,
        }
        if config:
            self.cfg.update(config)
        self._s = RealtimeSnapshot()
        self._last_focus = None
        self._last_gyro = None
        self._event_warnings: list[str] = []
        self._low_fi_since = None
        self._recover_streak = 0
        self._stable_streak = 0
        self._stream_was_inactive = True
        self._stream_epoch = 0
        self._epoch_attention_ts = None
        self._epoch_motion_ts = None

    def _age(self, now, last):
        return None if last is None else max(0, now - last)

    def _mark_epoch_input(self, algo: str, now_ms: int):
        if algo == 'attention':
            self._epoch_attention_ts = now_ms
        elif algo == 'gyroscope':
            self._epoch_motion_ts = now_ms

    def ingest_events(self, events: list[dict], now_ms: int) -> None:
        s = self._s
        for e in events:
            if e.get('type') == 'device_status':
                s.device_connected = bool(e.get('device_connected', False))
                s.bridge_alive = bool(e.get('bridge_alive', False))
                continue
            if e.get('type') != 'algorithm_frame':
                continue
            s.last_algorithm_update_ms = now_ms
            algo = e.get('algorithm')
            d = e.get('data', {})
            if algo == 'attention' and d.get('attention') is not None:
                s.attention = int(d['attention'])
                s.attention_last_update_ms = now_ms
                s.attention_seen_once = True
                self._mark_epoch_input('attention', now_ms)
            if algo == 'gyroscope':
                fx, fy = d.get('focus_x'), d.get('focus_y')
                gx, gy, gz = d.get('gyro_x'), d.get('gyro_y'), d.get('gyro_z')
                if fx is not None and fy is not None:
                    if self._last_focus is not None and abs(fx - self._last_focus[0]) + abs(fy - self._last_focus[1]) > self.cfg['focus_jump_threshold']:
                        self._event_warnings.append('focus_jump')
                    s.focus_x = fx
                    s.focus_y = fy
                    s.focus_last_update_ms = now_ms
                    s.focus_seen_once = True
                    self._last_focus = (fx, fy)
                if None not in (gx, gy, gz):
                    if self._last_gyro is not None and max(abs(gx - self._last_gyro[0]), abs(gy - self._last_gyro[1]), abs(gz - self._last_gyro[2])) > self.cfg['gyro_spike_threshold']:
                        self._event_warnings.append('gyro_spike')
                    s.gyro_x = gx
                    s.gyro_y = gy
                    s.gyro_z = gz
                    s.gyro_last_update_ms = now_ms
                    s.gyro_seen_once = True
                    self._last_gyro = (gx, gy, gz)
                self._mark_epoch_input('gyroscope', now_ms)

    def _update_control_state(self, s: RealtimeSnapshot, now_ms: int) -> None:
        if not s.stream_alive:
            s.control_state = 'NO_SIGNAL'
            return
        if not s.attention_seen_once:
            s.control_state = 'WARMUP'
            return
        if s.recovering:
            s.control_state = 'RECOVERING'
            return
        if s.quality == 'error' or not s.control_data_valid:
            s.control_state = 'SIGNAL_WARNING'
            return

        fi = s.fi
        if fi < 40:
=======
    def __init__(self, config:dict|None=None):
        self.cfg={'attention_fresh_ms':1500,'attention_lost_ms':5000,'gyro_fresh_ms':500,'gyro_lost_ms':2000,'focus_fresh_ms':500,'focus_lost_ms':2000,'algorithm_fresh_ms':500,'algorithm_lost_ms':2000,'focus_jump_threshold':200.0,'gyro_spike_threshold':80.0,'min_sqi':0.45,'warning_sqi':0.8,'error_sqi':0.4,'fatigued_enter_ms':9000,'fatigued_exit_ms':3000,'stable_enter_ticks':3,'stable_exit_threshold':55,'stable_enter_threshold':60,'warning_allows_fi_valid':False}
        if config: self.cfg.update(config)
        self._s=RealtimeSnapshot(); self._last_focus=None; self._last_gyro=None
        self._low_fi_since=None; self._stable_streak=0; self._recover_streak=0
        self._event_warnings=[]

    def ingest_events(self,events:list[dict],now_ms:int)->None:
        s=self._s
        for e in events:
            if e.get('type')=='device_status': s.device_connected=bool(e.get('device_connected',False)); s.bridge_alive=bool(e.get('bridge_alive',False))
            elif e.get('type')=='algorithm_frame':
                s.last_algorithm_update_ms=now_ms; algo=e.get('algorithm'); d=e.get('data',{})
                if algo=='attention' and d.get('attention') is not None: s.attention=int(d['attention']); s.attention_last_update_ms=now_ms; s.attention_seen_once=True
                if algo=='gyroscope':
                    fx,fy=d.get('focus_x'),d.get('focus_y'); gx,gy,gz=d.get('gyro_x'),d.get('gyro_y'),d.get('gyro_z')
                    if fx is not None and fy is not None:
                        if self._last_focus is not None and abs(fx-self._last_focus[0])+abs(fy-self._last_focus[1])>self.cfg['focus_jump_threshold']: self._event_warnings.append('focus_jump')
                        s.focus_x=fx; s.focus_y=fy; s.focus_last_update_ms=now_ms; s.focus_seen_once=True; self._last_focus=(fx,fy)
                    if None not in (gx,gy,gz):
                        if self._last_gyro is not None and max(abs(gx-self._last_gyro[0]),abs(gy-self._last_gyro[1]),abs(gz-self._last_gyro[2]))>self.cfg['gyro_spike_threshold']: self._event_warnings.append('gyro_spike')
                        s.gyro_x=gx; s.gyro_y=gy; s.gyro_z=gz; s.gyro_last_update_ms=now_ms; s.gyro_seen_once=True; self._last_gyro=(gx,gy,gz)

    def _age(self,now,last): return None if last is None else max(0,now-last)

    def _update_control_state(self,s:RealtimeSnapshot,now_ms:int)->None:
        if not s.attention_seen_once:
            s.control_state='WARMUP'; return
        if s.quality=='error' or not s.stream_alive:
            s.control_state='NO_SIGNAL'; return
        if s.fi_provisional or not s.training_data_valid or s.quality=='warning':
            s.control_state='SIGNAL_WARNING'; return
        fi=s.fi
        if fi<40:
>>>>>>> main
            self._low_fi_since = self._low_fi_since or now_ms
        else:
            self._low_fi_since = None

        low_dur = 0 if self._low_fi_since is None else now_ms - self._low_fi_since
        can_fatigue = s.control_data_valid and s.training_data_valid and s.fi_valid and s.quality == 'ok'
        if can_fatigue and low_dur >= self.cfg['fatigued_enter_ms']:
            s.control_state = 'FATIGUED'
            self._recover_streak = 0
            return
<<<<<<< codex/fix-datacenter-and-cli-debug-outputs-xjefpe

        if s.control_state == 'FATIGUED':
            if fi >= 45:
                self._recover_streak += 1
            else:
                self._recover_streak = 0
            if self._recover_streak * 100 >= self.cfg['fatigued_exit_ms']:
                s.control_state = 'DISTRACTED'
            return

        if fi >= self.cfg['stable_enter_threshold']:
            self._stable_streak += 1
        elif fi < self.cfg['stable_exit_threshold']:
            self._stable_streak = 0

        if self._stable_streak >= self.cfg['stable_enter_ticks']:
            s.control_state = 'STABLE_FOCUS'
        elif fi < 40:
            s.control_state = 'LOW_FOCUS'
        elif fi < 60:
            s.control_state = 'DISTRACTED'
        else:
            s.control_state = 'DISTRACTED'

    def tick(self, now_ms: int) -> RealtimeSnapshot:
        s = self._s
        s.now_ms = now_ms
        s.warning_flags = list(self._event_warnings)
        s.error_flags = []
        self._event_warnings = []

        s.attention_age_ms = self._age(now_ms, s.attention_last_update_ms)
        s.gyro_age_ms = self._age(now_ms, s.gyro_last_update_ms)
        s.focus_age_ms = self._age(now_ms, s.focus_last_update_ms)
        s.last_algorithm_age_ms = self._age(now_ms, s.last_algorithm_update_ms)
        s.attention_seen_once = bool(s.attention_seen_once)
        s.focus_seen_once = bool(s.focus_seen_once)
        s.gyro_seen_once = bool(s.gyro_seen_once)

        s.attention_fresh = s.attention_age_ms is not None and s.attention_age_ms <= self.cfg['attention_fresh_ms']
        s.gyro_fresh = s.gyro_age_ms is not None and s.gyro_age_ms <= self.cfg['gyro_fresh_ms']
        s.focus_fresh = s.focus_age_ms is not None and s.focus_age_ms <= self.cfg['focus_fresh_ms']

        s.stream_alive = s.last_algorithm_age_ms is not None and s.last_algorithm_age_ms <= self.cfg['algorithm_lost_ms']
        s.sensor_stream_active = s.last_algorithm_age_ms is not None and s.last_algorithm_age_ms <= self.cfg['algorithm_fresh_ms']

        if self._stream_was_inactive and s.stream_alive:
            self._stream_epoch += 1
            s.recovering = True
            self._epoch_attention_ts = None
            self._epoch_motion_ts = None
            self._low_fi_since = None
            self._stable_streak = 0
        elif not s.stream_alive:
            s.recovering = False
            self._low_fi_since = None
            self._stable_streak = 0
        else:
            s.recovering = self._epoch_attention_ts is None or not s.attention_fresh
        self._stream_was_inactive = not s.stream_alive
        s.stream_epoch = self._stream_epoch

        if not s.attention_seen_once:
            s.warning_flags.append('attention_missing')
        elif s.attention_age_ms and s.attention_age_ms > self.cfg['attention_lost_ms']:
            s.error_flags.append('attention_lost')
        elif s.attention_age_ms and s.attention_age_ms > self.cfg['attention_fresh_ms']:
            s.warning_flags.append('attention_stale')

        if s.gyro_seen_once and s.gyro_age_ms and s.gyro_age_ms > self.cfg['gyro_lost_ms']:
            s.error_flags.append('gyro_lost')
        elif s.gyro_seen_once and s.gyro_age_ms and s.gyro_age_ms > self.cfg['gyro_fresh_ms']:
            s.warning_flags.append('gyro_stale')

        if s.focus_seen_once and s.focus_age_ms and s.focus_age_ms > self.cfg['focus_lost_ms']:
            s.warning_flags.append('focus_lost')
        elif s.focus_seen_once and s.focus_age_ms and s.focus_age_ms > self.cfg['focus_fresh_ms']:
            s.warning_flags.append('focus_stale')

        if not s.device_connected:
            s.error_flags.append('device_disconnected')
        if not s.stream_alive:
            s.error_flags.append('stream_inactive')

        sqi = 1.0
        for r in set(s.warning_flags):
            sqi -= 0.08 if r in ('attention_stale', 'gyro_stale', 'focus_stale') else 0.15
        for _ in set(s.error_flags):
            sqi -= 0.35
        s.sqi = max(0.0, min(1.0, sqi))
        if s.error_flags or s.sqi < self.cfg['error_sqi']:
            s.quality = 'error'
        elif s.warning_flags or s.sqi < self.cfg['warning_sqi']:
            s.quality = 'warning'
        else:
            s.quality = 'ok'
        s.quality_reasons = list(dict.fromkeys(s.error_flags + s.warning_flags))

        s.fi = float(s.attention if s.attention is not None else 0)
        has_new_attention_this_epoch = self._epoch_attention_ts is not None
        motion_fresh = s.gyro_fresh or s.focus_fresh
        s.display_data_available = bool(s.device_connected and s.stream_alive and (s.attention_seen_once or s.focus_seen_once or s.gyro_seen_once))
        s.training_data_valid = bool(
            s.device_connected and s.stream_alive and has_new_attention_this_epoch and s.attention_fresh and
            motion_fresh and not s.error_flags and s.sqi >= self.cfg['min_sqi']
        )
        s.control_data_valid = bool(s.training_data_valid and s.quality == 'ok' and not s.recovering)
        s.fi_valid = bool(s.training_data_valid and (s.quality == 'ok' or self.cfg.get('allow_stale_attention_fi_valid', False)))
        if s.quality == 'warning' and not self.cfg.get('warning_allows_fi_valid', False):
            s.fi_valid = False
        s.fi_provisional = bool(not s.fi_valid)

        self._update_control_state(s, now_ms)
=======
        if fi>=self.cfg['stable_enter_threshold']:
            self._stable_streak+=1
        elif fi<self.cfg['stable_exit_threshold']:
            self._stable_streak=0
        if self._stable_streak>=self.cfg['stable_enter_ticks']: s.control_state='STABLE_FOCUS'
        elif fi<40: s.control_state='LOW_FOCUS'
        elif fi<60: s.control_state='DISTRACTED'

    def tick(self,now_ms:int)->RealtimeSnapshot:
        s=self._s; s.now_ms=now_ms; s.warning_flags=list(self._event_warnings); s.error_flags=[]; self._event_warnings=[]
        s.attention_age_ms=self._age(now_ms,s.attention_last_update_ms); s.gyro_age_ms=self._age(now_ms,s.gyro_last_update_ms); s.focus_age_ms=self._age(now_ms,s.focus_last_update_ms); s.last_algorithm_age_ms=self._age(now_ms,s.last_algorithm_update_ms)
        s.attention_fresh=(s.attention_age_ms is not None and s.attention_age_ms<=self.cfg['attention_fresh_ms']); s.gyro_fresh=(s.gyro_age_ms is not None and s.gyro_age_ms<=self.cfg['gyro_fresh_ms']); s.focus_fresh=(s.focus_age_ms is not None and s.focus_age_ms<=self.cfg['focus_fresh_ms'])
        if not s.attention_seen_once: s.warning_flags.append('attention_missing')
        elif s.attention_age_ms and s.attention_age_ms>self.cfg['attention_lost_ms']: s.error_flags.append('attention_lost')
        elif s.attention_age_ms and s.attention_age_ms>self.cfg['attention_fresh_ms']: s.warning_flags.append('attention_stale')
        if s.gyro_seen_once and s.gyro_age_ms and s.gyro_age_ms>self.cfg['gyro_lost_ms']: s.error_flags.append('gyro_lost')
        elif s.gyro_seen_once and s.gyro_age_ms and s.gyro_age_ms>self.cfg['gyro_fresh_ms']: s.warning_flags.append('gyro_stale')
        if s.focus_seen_once and s.focus_age_ms and s.focus_age_ms>self.cfg['focus_lost_ms']: s.warning_flags.append('focus_lost')
        elif s.focus_seen_once and s.focus_age_ms and s.focus_age_ms>self.cfg['focus_fresh_ms']: s.warning_flags.append('focus_stale')
        s.stream_alive=s.last_algorithm_age_ms is not None and s.last_algorithm_age_ms<=self.cfg['algorithm_lost_ms']; s.sensor_stream_active=s.last_algorithm_age_ms is not None and s.last_algorithm_age_ms<=self.cfg['algorithm_fresh_ms']
        if not s.device_connected: s.error_flags.append('device_disconnected')
        if not s.stream_alive: s.error_flags.append('stream_inactive')
        # sqi dynamic
        sqi=1.0
        for r in set(s.warning_flags): sqi-=0.08 if r in ('attention_stale','gyro_stale','focus_stale') else 0.15
        for r in set(s.error_flags): sqi-=0.35
        s.sqi=max(0.0,min(1.0,sqi))
        if s.error_flags or s.sqi<self.cfg['error_sqi']: s.quality='error'
        elif s.warning_flags or s.sqi<self.cfg['warning_sqi']: s.quality='warning'
        else: s.quality='ok'
        s.quality_reasons=list(dict.fromkeys(s.error_flags+s.warning_flags))
        s.fi=float(s.attention if s.attention is not None else 0)
        s.training_data_valid=bool(
            s.device_connected and s.stream_alive and s.attention_seen_once and s.attention is not None and
            (s.attention_age_ms is not None and s.attention_age_ms<=self.cfg['attention_lost_ms']) and
            (s.gyro_seen_once or s.focus_seen_once) and not s.error_flags and s.sqi>=self.cfg['min_sqi']
        )
        s.fi_provisional=bool(not s.attention_seen_once and (s.gyro_seen_once or s.focus_seen_once))
        s.fi_valid=bool(s.training_data_valid and s.quality=='ok')
        if s.quality=='warning' and not self.cfg.get('warning_allows_fi_valid',False):
            s.fi_valid=False
            s.fi_provisional=True
        elif not s.fi_valid:
            s.fi_provisional=True
        self._update_control_state(s,now_ms)
>>>>>>> main
        return s

    def get_snapshot(self) -> RealtimeSnapshot:
        return self._s
