import json
from pathlib import Path
from .models import AppState,RealtimeSnapshot
from .input import InputManager
from .coordinates import CoordinateMapper
from .assets import AssetManager
from .session import SessionManager
from .calibration import CalibrationManager
from .quality import QualityManager
from .focus import FocusModel
from .difficulty import StateMachine,DifficultyController
from .game_api import GameContext
from games.empty_game import EmptyGame
class AppCore:
    def __init__(self,data_bridge,config_path='config/default_config.json'):
        self.data_bridge=data_bridge; self.input_manager=InputManager(); self.coordinate_mapper=CoordinateMapper(); self.asset_manager=AssetManager('.'); self.session_manager=SessionManager(); self.calibration_manager=CalibrationManager();
        cfg=Path(config_path); self.config=json.loads(cfg.read_text(encoding='utf-8')) if cfg.exists() else {}
        q=self.config.get('quality',{}); self.quality_manager=QualityManager(**q); self.focus_model=FocusModel(); self.state_machine=StateMachine(); self.difficulty_controller=DifficultyController(); self.current_game=None; self.app_state=AppState.BOOTING.value
    def start(self): self.data_bridge.start(); self.app_state=AppState.CONNECTED.value
    def stop(self): self.cleanup(); self.app_state=AppState.EXITING.value
    def load_game(self,game):
        ctx=GameContext(self.data_bridge,self.input_manager,self.coordinate_mapper,self.asset_manager,self.session_manager,self.quality_manager,self.focus_model,self.state_machine,self.difficulty_controller,self.config)
        game.setup(ctx); self.current_game=game
    def start_game(self,game_id='empty_game'):
        if game_id=='empty_game' and not self.current_game: self.load_game(EmptyGame())
        self.session_manager.start_session(game_id); self.current_game.start(); self.app_state=AppState.GAME_RUNNING.value
    def pause_game(self):
        if self.current_game: self.current_game.pause(); self.app_state=AppState.GAME_PAUSED.value
    def resume_game(self):
        if self.current_game: self.current_game.resume(); self.app_state=AppState.GAME_RUNNING.value
    def end_game(self,reason='normal'):
        if self.current_game: self.current_game.end(reason); self.session_manager.end_session(reason,self.current_game.get_metrics().__dict__)
    def handle_input(self,event): self.input_manager.push_event(event)
    def tick(self,dt_ms):
        snap=RealtimeSnapshot.from_dict(self.data_bridge.get_snapshot())
        q=self.quality_manager.evaluate(snap); m=self.current_game.get_metrics() if self.current_game else None; f=self.focus_model.compute(snap,m,q); st=self.state_machine.update(f,q); lvl=self.difficulty_controller.update(m,st)
        if self.current_game:
            for ev in self.input_manager.poll_events(): self.current_game.handle_input(ev)
            self.current_game.update(dt_ms,snap)
        return {"app_state":self.app_state,"snapshot":snap.to_dict(),"quality":q.__dict__,"focus":f.__dict__,"state":st,"difficulty":lvl,"current_game":getattr(self.current_game,'game_id',None)}
    def get_status(self): return {"app_state":self.app_state,"current_game":getattr(self.current_game,'game_id',None)}
    def cleanup(self):
        if self.current_game: self.current_game.cleanup()
        self.session_manager.close(); self.data_bridge.close()
