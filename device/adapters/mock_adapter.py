import math

class MockAdapter:
    def __init__(self):
        self.t=0.0
        self.device_connected=True
    def poll(self,dt_ms:int)->list[dict]:
        self.t += dt_ms/1000.0
        events=[{'type':'device_status','device_connected':self.device_connected,'bridge_alive':True}]
        # 高频 gyro/focus ~20Hz
        events.append({'type':'algorithm_frame','algorithm':'gyroscope','ts_ms':None,
                       'data':{'focus_x':960+120*math.sin(self.t),'focus_y':540+80*math.cos(self.t),
                               'gyro_x':255+20*math.sin(self.t*2), 'gyro_y':255+20*math.cos(self.t*2), 'gyro_z':176+10*math.sin(self.t)}})
        # 低频 attention ~1Hz
        if int(self.t*10)%10==0:
            events.append({'type':'algorithm_frame','algorithm':'attention','ts_ms':None,'data':{'attention':60+int(10*math.sin(self.t/2))}})
        # occasional jumps/spikes
        if int(self.t)==6:
            events.append({'type':'algorithm_frame','algorithm':'gyroscope','ts_ms':None,
                           'data':{'focus_x':1400,'focus_y':200,'gyro_x':500,'gyro_y':100,'gyro_z':400}})
        return events
