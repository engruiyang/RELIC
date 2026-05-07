from dataclasses import dataclass
from typing import Any
from .models import GameMetrics
@dataclass
class GameContext:
    data_bridge:Any; input_manager:Any; coordinate_mapper:Any; asset_manager:Any; session_manager:Any; quality_manager:Any; focus_model:Any; state_machine:Any; difficulty_controller:Any; config:dict
class BaseGame:
    game_id='base'; display_name='Base Game'
    def __init__(self): self.context=None; self.paused=False
    def setup(self,context:GameContext)->None: self.context=context
    def start(self)->None: ...
    def pause(self)->None: self.paused=True
    def resume(self)->None: self.paused=False
    def update(self,dt_ms:int,snapshot)->None: ...
    def handle_input(self,event)->None: ...
    def end(self,reason:str='normal')->None: ...
    def cleanup(self)->None: self.context=None
    def get_metrics(self)->GameMetrics: return GameMetrics()
