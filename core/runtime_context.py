from dataclasses import dataclass
from core.system_clock import SystemClock

@dataclass
class RuntimeContext:
    clock:SystemClock
    config:dict
