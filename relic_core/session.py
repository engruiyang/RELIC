from __future__ import annotations
import json,time
from pathlib import Path
from datetime import datetime,timezone
from .models import RealtimeSnapshot, SessionInfo

def now_iso(): return datetime.now(timezone.utc).isoformat()
class SessionManager:
    def __init__(self,base_dir:str='logs/app'):
        self.base_dir=Path(base_dir); self.base_dir.mkdir(parents=True,exist_ok=True); self.info=None; self._f=None; self._closed=False
    def start_session(self,game_id=None):
        sid=datetime.now().strftime('%Y%m%d_%H%M%S')
        ev=self.base_dir/f'session_{sid}_game.jsonl'; sm=self.base_dir/f'session_{sid}_summary.json'
        self._f=ev.open('a',encoding='utf-8')
        self.info=SessionInfo(sid,now_iso(),None,game_id,str(self.base_dir),str(ev),str(sm)); self._closed=False; return self.info
    def write_game_event(self,event_type,snapshot=None,payload=None,extra=None):
        if not self.info: self.start_session('unknown')
        s=RealtimeSnapshot.from_dict(snapshot) if isinstance(snapshot,dict) else snapshot if isinstance(snapshot,RealtimeSnapshot) else RealtimeSnapshot()
        row={"timestamp_utc":now_iso(),"monotonic_ms":int(time.monotonic()*1000),"session_id":self.info.session_id,"game_id":self.info.game_id,"event_type":event_type,"attention_value":s.attention_value,"attention_age_ms":s.attention_age_ms,"focus_x":s.focus_x,"focus_y":s.focus_y,"gyro_x":s.gyro_x,"gyro_y":s.gyro_y,"gyro_z":s.gyro_z,"payload":payload or {}}
        if extra: row.update(extra)
        self._f.write(json.dumps(row,ensure_ascii=False)+'\n'); self._f.flush()
    def end_session(self,reason='normal',metrics=None):
        if not self.info: return
        self.info.end_time_utc=now_iso(); summary={"session_id":self.info.session_id,"start_time_utc":self.info.start_time_utc,"end_time_utc":self.info.end_time_utc,"reason":reason,"game_id":self.info.game_id,"metrics":metrics or {}}
        Path(self.info.summary_path).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    def close(self):
        if self._closed: return
        if self._f: self._f.close(); self._f=None
        self._closed=True
