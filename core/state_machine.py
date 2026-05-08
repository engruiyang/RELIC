from enum import Enum

class SystemState(str, Enum):
    BOOTING='BOOTING'; NO_USER='NO_USER'; USER_READY='USER_READY'; PLATFORM_WAITING='PLATFORM_WAITING'; DEVICE_WAITING='DEVICE_WAITING'; DEVICE_CONNECTED='DEVICE_CONNECTED'; CALIBRATING='CALIBRATING'; CALIBRATION_FAILED='CALIBRATION_FAILED'; READY='READY'; TRAINING='TRAINING'; PAUSED='PAUSED'; WARNING='WARNING'; ERROR='ERROR'; SHUTDOWN='SHUTDOWN'

class StateMachine:
    def __init__(self): self.state=SystemState.BOOTING
    def transition(self,new_state:SystemState)->tuple[SystemState,SystemState]:
        old=self.state; self.state=new_state; return old,new_state
