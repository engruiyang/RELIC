from core.state_machine import StateMachine, SystemState
from core.system_clock import SystemClock
from core.runtime_context import RuntimeContext
from config.config_loader import load_config
from device.device_manager import DeviceManager
from data.data_center import DataCenter

class AppController:
    def __init__(self):
        self.config=load_config(); self.clock=SystemClock(); self.context=RuntimeContext(clock=self.clock,config=self.config)
        mode=self.config.get('mock_mode','normal')
        self.state_machine=StateMachine(); self.device_manager=DeviceManager(mode=mode); self.data_center=DataCenter(self.config.get('data_center',{})); self.tick_count=0
    def start(self)->None:
        old,new=self.state_machine.transition(SystemState.NO_USER); print(f'[AppController] state: {old.value} -> {new.value}')
    def tick(self,dt_ms:int=50)->dict:
        now=self.clock.monotonic_ms(); events=self.device_manager.poll_events(dt_ms); self.data_center.ingest_events(events,now); snap=self.data_center.tick(now); self.tick_count+=1; return snap.to_dict()
    def shutdown(self)->None:
        old,new=self.state_machine.transition(SystemState.SHUTDOWN); print(f'[AppController] state: {old.value} -> {new.value}')
