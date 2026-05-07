import time
from .models import FocusState, GameMetrics
class StateMachine:
    def __init__(self): self.history=[]; self.current=FocusState.UNKNOWN.value
    def update(self,focus,quality=None,now_ms=None):
        if quality and quality.status=='error': st=FocusState.NO_SIGNAL.value
        elif focus.fi>=80: st=FocusState.HIGH_FOCUS.value
        elif focus.fi>=60: st=FocusState.STABLE_FOCUS.value
        elif focus.fi>=40: st=FocusState.DISTRACTED.value
        else: st=FocusState.FATIGUED.value
        self.current=st; self.history.append((now_ms or int(time.monotonic()*1000),st)); return st
class DifficultyController:
    def __init__(self,min_level=1,max_level=5): self.level=1; self.min=min_level; self.max=max_level; self.last_change_ms=0
    def update(self,metrics,state,now_ms=None):
        now=now_ms or int(time.monotonic()*1000)
        if now-self.last_change_ms<10000: return self.level
        if not metrics: return self.level
        m=metrics if isinstance(metrics,GameMetrics) else GameMetrics(**metrics)
        if None in (m.accuracy,m.rt_stability,m.si_window): return self.level
        perf=0.4*m.accuracy+0.3*m.rt_stability+0.3*m.si_window
        if state in ('HIGH_FOCUS','STABLE_FOCUS') and perf>0.72: self.level=min(self.max,self.level+1); self.last_change_ms=now
        elif state in ('DISTRACTED','FATIGUED','NO_SIGNAL') or perf<0.45: self.level=max(self.min,self.level-1); self.last_change_ms=now
        return self.level
    def get_level(self): return self.level
    def get_params(self): return {"level":self.level}
