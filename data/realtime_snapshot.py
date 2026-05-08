from dataclasses import dataclass, field

@dataclass
class RealtimeSnapshot:
    attention:int|None=None
    focus_x:float|None=None
    focus_y:float|None=None
    gyro_x:float|None=None
    gyro_y:float|None=None
    gyro_z:float|None=None
    extra:dict=field(default_factory=dict)
