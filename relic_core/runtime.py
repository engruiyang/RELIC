import json
from pathlib import Path
from .models import AppState, RealtimeSnapshot, StreamState
from .input import InputManager
from .coordinates import CoordinateMapper
from .assets import AssetManager
from .session import SessionManager
from .calibration import CalibrationManager
from .quality import QualityManager
from .focus import FocusModel
from .difficulty import StateMachine, DifficultyController
from .game_api import GameContext
from games.empty_game import EmptyGame

class AppCore:
    def __init__(self,data_bridge,config_path='config/default_config.json'):
        self.data_bridge=data_bridge; self.input_manager=InputManager(); self.coordinate_mapper=CoordinateMapper(); self.asset_manager=AssetManager('.'); self.session_manager=SessionManager(); self.calibration_manager=CalibrationManager()
        cfg=Path(config_path); self.config=json.loads(cfg.read_text(encoding='utf-8')) if cfg.exists() else {}
        self.quality_manager=QualityManager(**self.config.get('quality',{})); self.focus_model=FocusModel(); self.state_machine=StateMachine(); self.difficulty_controller=DifficultyController(); self.current_game=None; self.app_state=AppState.BOOTING.value
    def start(self): self.data_bridge.start(); self.app_state=AppState.CONNECTED.value
    def stop(self): self.cleanup(); self.app_state=AppState.EXITING.value
    def load_game(self,game): game.setup(GameContext(self.data_bridge,self.input_manager,self.coordinate_mapper,self.asset_manager,self.session_manager,self.quality_manager,self.focus_model,self.state_machine,self.difficulty_controller,self.config)); self.current_game=game
    def start_game(self,game_id='empty_game'):
        if game_id=='empty_game' and not self.current_game: self.load_game(EmptyGame())
        self.session_manager.start_session(game_id); self.current_game.start(); self.app_state=AppState.GAME_RUNNING.value
    def end_game(self,reason='normal'):
        if self.current_game: self.current_game.end(reason); self.session_manager.end_session(reason,self.current_game.get_metrics().__dict__)
    def _compute_stream_state(self,s:RealtimeSnapshot):
        if not s.bridge_connected: return StreamState.BRIDGE_DISCONNECTED.value, False
        if not s.bridge_alive: return StreamState.BRIDGE_DEAD.value, False
        if s.last_algorithm_msg_age_ms is None:
            att=s.attention_age_ms if s.attention_age_ms is not None else 999999
            gy=s.gyro_age_ms if s.gyro_age_ms is not None else 999999
            active=(att<=8000) or (gy<=3000)
            if att<=3000 or gy<=3000: return StreamState.INITIAL_WAITING.value, active
            return (StreamState.PARTIAL_STALE.value if active else StreamState.STREAM_INACTIVE.value), active
        if s.last_algorithm_msg_age_ms<=3000:
            if (s.attention_age_ms and s.attention_age_ms>3000) or (s.gyro_age_ms and s.gyro_age_ms>500):
                return StreamState.PARTIAL_STALE.value, True
            return StreamState.ACTIVE.value, True
        return StreamState.STREAM_INACTIVE.value, False
    def tick(self,dt_ms):
        raw=self.data_bridge.get_snapshot(); raw=dict(raw) if isinstance(raw,dict) else {}
        raw['bridge_connected']=bool(raw.get('connected',False)); raw['bridge_alive']=bool(raw.get('bridge_alive',getattr(self.data_bridge,'is_alive',lambda:raw.get('connected',False))()))
        snap=RealtimeSnapshot.from_dict(raw)
        stream_state,sensor_active=self._compute_stream_state(snap); snap.sensor_stream_active=sensor_active
        q=self.quality_manager.evaluate(snap)
        training_valid=bool(snap.bridge_connected and snap.bridge_alive and sensor_active and q.status!='error')
        snap.training_data_valid=training_valid
        m=self.current_game.get_metrics() if self.current_game else None; f=self.focus_model.compute(snap,m,q); st=self.state_machine.update(f,q,training_data_valid=training_valid,stream_state=stream_state); lvl=self.difficulty_controller.update(m,st)
        if self.current_game:
            for ev in self.input_manager.poll_events(): self.current_game.handle_input(ev)
            self.current_game.update(dt_ms,snap)
        return {"app_state":self.app_state,"snapshot":snap.to_dict(),"quality":q.__dict__,"focus":f.__dict__,"focus_state":st,"stream_state":stream_state,"bridge_connected":snap.bridge_connected,"bridge_alive":snap.bridge_alive,"sensor_stream_active":sensor_active,"training_data_valid":training_valid,"difficulty":lvl,"current_game":getattr(self.current_game,'game_id',None)}
    def cleanup(self):
        if self.current_game: self.current_game.cleanup()
        self.session_manager.close(); self.data_bridge.close()
