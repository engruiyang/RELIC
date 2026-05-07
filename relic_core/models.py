from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
import time

class AppState(str, Enum):
    BOOTING="BOOTING"; MAIN_MENU="MAIN_MENU"; CONNECTING="CONNECTING"; CONNECTED="CONNECTED"; QUICK_CHECK="QUICK_CHECK"; CALIBRATING="CALIBRATING"; GAME_SELECT="GAME_SELECT"; GAME_RUNNING="GAME_RUNNING"; GAME_PAUSED="GAME_PAUSED"; REPORT_VIEW="REPORT_VIEW"; ERROR="ERROR"; EXITING="EXITING"
class FocusState(str, Enum):
    HIGH_FOCUS="HIGH_FOCUS"; STABLE_FOCUS="STABLE_FOCUS"; DISTRACTED="DISTRACTED"; FATIGUED="FATIGUED"; NO_SIGNAL="NO_SIGNAL"; UNKNOWN="UNKNOWN"

@dataclass
class RealtimeSnapshot:
    connected: bool=False; bridge_alive: bool|None=None; layout_type:int|None=None; last_msg:str|None=None; last_algorithm_name:str|None=None
    attention_value:int|None=None; attention_valid:bool=False; attention_age_ms:int|None=None
    focus_x:float|None=None; focus_y:float|None=None; focus_area_x:float|None=None; focus_area_y:float|None=None; focus_area_width:float|None=None; focus_area_height:float|None=None
    gyro_x:float|None=None; gyro_y:float|None=None; gyro_z:float|None=None; gyro_valid:bool=False; gyro_age_ms:int|None=None
    blink_state:str|int|None=None; device_connected:bool|None=None; device_wear:bool|None=None; battery:int|None=None; sample_rate:int|None=None
    @classmethod
    def from_dict(cls,d:dict[str,Any])->"RealtimeSnapshot":
        data=dict(d)
        return cls(**{k:data.get(k,getattr(cls,k,None)) for k in cls.__dataclass_fields__.keys()})
    def to_dict(self)->dict[str,Any]: return asdict(self)

@dataclass
class InputEvent:
    event_type:str; timestamp_ms:int=field(default_factory=lambda:int(time.monotonic()*1000)); x:float|None=None; y:float|None=None; key:str|None=None; button:str|None=None; payload:dict[str,Any]=field(default_factory=dict)

@dataclass
class QualityResult:
    sqi:float; status:str; reasons:list[str]=field(default_factory=list)
    def __post_init__(self): self.sqi=max(0.0,min(1.0,float(self.sqi)))

@dataclass
class FocusResult:
    fi:float; s_eeg:float; s_imu:float; s_b:float; valid:bool=True; reasons:list[str]=field(default_factory=list)
    def __post_init__(self): self.fi=max(0.0,min(100.0,float(self.fi)))

@dataclass
class GameMetrics:
    accuracy:float|None=None; omission:float|None=None; false_action:float|None=None; rt_stability:float|None=None; si_window:float|None=None; extra:dict[str,Any]=field(default_factory=dict)

@dataclass
class SessionInfo:
    session_id:str; start_time_utc:str; end_time_utc:str|None; game_id:str|None; base_dir:str; event_log_path:str; summary_path:str
