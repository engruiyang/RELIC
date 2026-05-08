from core.state_machine import StateMachine, SystemState
from core.system_clock import SystemClock
from core.runtime_context import RuntimeContext
from config.config_loader import load_config
from platform.platform_gateway import PlatformGateway
from device.device_manager import DeviceManager
from data.data_center import DataCenter
from user.user_manager import UserManager
from user.profile_manager import ProfileManager
from calibration.calibration_manager import CalibrationManager
from session.session_manager import SessionManager
from game.game_manager import GameManager
from runtime.local_runtime import LocalRuntime
from storage.storage_manager import StorageManager

class AppController:
    def __init__(self):
        self.config=load_config(); self.clock=SystemClock(); self.context=RuntimeContext(clock=self.clock,config=self.config)
        self.state_machine=StateMachine(); self.platform_gateway=PlatformGateway(); self.device_manager=DeviceManager(); self.data_center=DataCenter(); self.user_manager=UserManager(); self.profile_manager=ProfileManager(); self.calibration_manager=CalibrationManager(); self.session_manager=SessionManager(); self.game_manager=GameManager(); self.runtime=LocalRuntime(); self.storage=StorageManager()
    def start(self)->None:
        old,new=self.state_machine.transition(SystemState.NO_USER)
        print(f'[AppController] state: {old.value} -> {new.value}')
    def shutdown(self)->None:
        old,new=self.state_machine.transition(SystemState.SHUTDOWN)
        print(f'[AppController] state: {old.value} -> {new.value}')
