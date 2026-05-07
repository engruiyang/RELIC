from __future__ import annotations
from typing import Protocol, Any
import threading, time, math

class DataBridgeProtocol(Protocol):
    def start(self)->None: ...
    def stop(self)->None: ...
    def get_snapshot(self)->dict: ...
    def close(self)->None: ...

class LiveDataBridgeAdapter:
    def __init__(self,host:str='127.0.0.1',port:int=8000,**kwargs:Any):
        self.host,self.port=host,port; self.kwargs=kwargs; self.client=None; self._t=None
    def start(self)->None:
        err=None
        for mod in ('relic_data_bridge','RELIC_MAIN'):
            try:
                m=__import__(mod,fromlist=['RelicClient']); C=getattr(m,'RelicClient'); break
            except Exception as e: err=e; C=None
        if C is None: raise RuntimeError(f'无法导入RelicClient: {err}')
        self.client=C(self.host,self.port,False,False,False,0,False)
        if hasattr(self.client,'connect'): self.client.connect()
        self._t=threading.Thread(target=getattr(self.client,'recv_loop'),daemon=True); self._t.start()
    def stop(self)->None:
        if self.client and hasattr(self.client,'close'): self.client.close()
    def get_snapshot(self)->dict:
        return self.client.get_snapshot() if self.client else {}
    def close(self)->None: self.stop()

class MockDataBridge:
    def __init__(self):
        self.running=False; self.t0=time.monotonic(); self.last_att=self.t0; self.last_gyro=self.t0; self.att=60; self.s={"connected":True,"attention_valid":True,"gyro_valid":True}
    def start(self)->None: self.running=True
    def stop(self)->None: self.running=False
    def tick(self,dt_ms:int=50)->None:
        n=time.monotonic(); t=n-self.t0
        if (n-self.last_gyro)>=0.05:
            self.s.update({"focus_area_x":0.0,"focus_area_y":0.0,"focus_area_width":1920.0,"focus_area_height":1080.0,"focus_x":960+220*math.sin(t/2),"focus_y":540+120*math.cos(t/2),"gyro_x":255+10*math.sin(t),"gyro_y":255+8*math.cos(t*1.2),"gyro_z":176+6*math.sin(t*0.7),"gyro_age_ms":int((time.monotonic()-n)*1000),"gyro_valid":True}); self.last_gyro=n
        if (n-self.last_att)>=1.0:
            self.att=max(0,min(100,self.att+int(5*math.sin(t))))
            self.s.update({"attention_value":self.att,"attention_valid":True,"attention_age_ms":0}); self.last_att=n
        else:
            self.s["attention_age_ms"]=int((n-self.last_att)*1000)
    def get_snapshot(self)->dict:
        if self.running: self.tick()
        return dict(self.s)
    def close(self)->None: self.stop()
