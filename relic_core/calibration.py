import json,time,statistics
from pathlib import Path
class CalibrationManager:
    def __init__(self,profile_dir='profiles'): self.profile_dir=Path(profile_dir); self.profile_dir.mkdir(parents=True,exist_ok=True)
    def _path(self,profile_id='default'): return self.profile_dir/f'{profile_id}_profile.json'
    def load_profile(self,profile_id='default'):
        p=self._path(profile_id)
        return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    def save_profile(self,profile,profile_id='default')->None: self._path(profile_id).write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf-8')
    def run_quick_check(self,snapshot_provider,duration_sec=3.0):
        end=time.monotonic()+duration_sec; at=[]; gy=[]; reasons=[]; connected=True
        while time.monotonic()<end:
            s=snapshot_provider(); connected=connected and bool(s.get('connected',False))
            if s.get('attention_value') is not None: at.append(s['attention_value'])
            if s.get('gyro_x') is not None and s.get('gyro_y') is not None and s.get('gyro_z') is not None: gy.append((s['gyro_x'],s['gyro_y'],s['gyro_z']))
            time.sleep(0.05)
        if not connected: reasons.append('disconnected')
        if not at: reasons.append('missing_attention')
        if not gy: reasons.append('missing_gyro')
        still=0.0
        if len(gy)>=2:
            dif=[abs(gy[i][0]-gy[i-1][0])+abs(gy[i][1]-gy[i-1][1])+abs(gy[i][2]-gy[i-1][2]) for i in range(1,len(gy))]
            still=max(0.0,min(1.0,1-statistics.mean(dif)/20))
        return {"passed":len([r for r in reasons if r=='disconnected'])==0,"reasons":reasons,"attention_samples":len(at),"gyro_samples":len(gy),"attention_baseline_mean":(statistics.mean(at) if at else None),"gyro_stillness_score":still,"duration_sec":duration_sec}
    def run_first_calibration(self,snapshot_provider,duration_sec=5.0): return self.run_quick_check(snapshot_provider,duration_sec)
