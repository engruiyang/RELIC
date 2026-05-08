from dataclasses import dataclass
@dataclass
class PlatformMessage:
    kind:str
    payload:dict
