import math

class MockAdapter:
    def __init__(self, mode:str='normal'):
        self.t=0.0
        self.device_connected=True
        self.mode=mode
        self._tick=0

    def poll(self,dt_ms:int)->list[dict]:
        self.t += dt_ms/1000.0
        self._tick += 1
        events=[{'type':'device_status','device_connected':self.device_connected,'bridge_alive':True}]

        if self.mode=='stream_drop' and self.t>5:
            return events
        if self.mode=='gyro_short_dropout' and 4.0<self.t<5.0:
            emit_attention=(self._tick % 10 == 0)
            if emit_attention:
                events.append({'type':'algorithm_frame','algorithm':'attention','data':{'attention':60+int(12*math.sin(self.t/2))}})
            return events

        gx=255+20*math.sin(self.t*2); gy=255+20*math.cos(self.t*2); gz=176+10*math.sin(self.t)
        fx=960+120*math.sin(self.t); fy=540+80*math.cos(self.t)
        if self.mode=='focus_jump' and 3.0<self.t<3.2: fx,fy=1450,150
        if self.mode=='gyro_spike' and 3.0<self.t<3.2: gx,gy,gz=600,50,430
        if self.mode=='mixed_warning' and 4.0<self.t<4.3: fx,fy,gx,gy,gz=1450,150,600,50,430

        events.append({'type':'algorithm_frame','algorithm':'gyroscope','data':{'focus_x':fx,'focus_y':fy,'gyro_x':gx,'gyro_y':gy,'gyro_z':gz}})

        emit_attention = (self._tick % 10 == 0)
        if self.mode=='attention_missing_start' and self.t<6: emit_attention=False
        if self.mode=='attention_short_dropout' and 4<self.t<6.6: emit_attention=False
        if self.mode=='attention_long_lost' and self.t>4: emit_attention=False

        if emit_attention:
            events.append({'type':'algorithm_frame','algorithm':'attention','data':{'attention':60+int(12*math.sin(self.t/2))}})
        return events
