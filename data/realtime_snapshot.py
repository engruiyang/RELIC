from dataclasses import dataclass, field

@dataclass
class RealtimeSnapshot:
    now_ms:int=0
    attention:int|None=None
    attention_last_update_ms:int|None=None
    attention_age_ms:int|None=None
    attention_fresh:bool=False
    attention_seen_once:bool=False

    gyro_x:float|None=None; gyro_y:float|None=None; gyro_z:float|None=None
    gyro_last_update_ms:int|None=None; gyro_age_ms:int|None=None; gyro_fresh:bool=False; gyro_seen_once:bool=False

    focus_x:float|None=None; focus_y:float|None=None
    focus_last_update_ms:int|None=None; focus_age_ms:int|None=None; focus_fresh:bool=False; focus_seen_once:bool=False

    last_algorithm_update_ms:int|None=None
    last_algorithm_age_ms:int|None=None

    device_connected:bool=False
    bridge_alive:bool=False
    stream_alive:bool=False
    sensor_stream_active:bool=False
    display_data_available:bool=False
    training_data_valid:bool=False
    control_data_valid:bool=False
    stream_epoch:int=0
    recovering:bool=False

    sqi:float=0.0
    quality:str='warning'
    quality_reasons:list[str]=field(default_factory=list)
    warning_flags:list[str]=field(default_factory=list)
    error_flags:list[str]=field(default_factory=list)

    fi:float=0.0
    fi_valid:bool=False
    fi_provisional:bool=True
    control_state:str='WARMUP'

    def to_dict(self)->dict:
        return self.__dict__.copy()
