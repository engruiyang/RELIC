from dataclasses import dataclass
@dataclass
class CalibrationProfile:
    profile_id:str='default'
    ready:bool=False
