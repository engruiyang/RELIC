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
from core.quality_gate import QualityGate


class AppController:
    def __init__(self):
        self.config = load_config()
        self.clock = SystemClock()
        self.context = RuntimeContext(clock=self.clock, config=self.config)
        self.state_machine = StateMachine()
        self.platform_gateway = PlatformGateway()
        mock_mode = self.config.get("mock", {}).get("mode", "normal")
        self.device_manager = DeviceManager(mock_mode=mock_mode)
        quality_cfg = self.config.get("mock", {}).get("thresholds_ms", {})
        self.data_center = DataCenter(
            attention_fresh_ms=quality_cfg.get("attention_fresh_ms", 1500),
            attention_lost_ms=quality_cfg.get("attention_lost_ms", 5000),
            gyro_fresh_ms=quality_cfg.get("gyro_fresh_ms", 500),
            gyro_lost_ms=quality_cfg.get("gyro_lost_ms", 2000),
        )
        storage_cfg = self.config.get("storage", {})
        self.storage = StorageManager(sqlite_path=storage_cfg.get("sqlite_path", "data/relic_local.db"))
        self.user_manager = UserManager(self.storage.sqlite)
        self.profile_manager = ProfileManager(self.storage.sqlite)
        self.calibration_manager = CalibrationManager()
        self.session_manager = SessionManager()
        self.game_manager = GameManager()
        self.runtime = LocalRuntime()
        self.quality_gate = QualityGate()
        self.current_user = None

    def _bootstrap_user(self) -> None:
        mode = self.config.get("user", {}).get("startup_mode", "demo")
        if mode == "guest":
            user = self.user_manager.enter_guest_mode()
        else:
            user = self.user_manager.ensure_demo_user()
            self.profile_manager.load_profile(user["user_id"])
        self.current_user = user
        old, new = self.state_machine.transition(SystemState.USER_READY)
        print(f"[AppController] state: {old.value} -> {new.value} user={user['user_id']} type={user['user_type']}")

    def start(self, ticks: int | None = None, debug: bool = True) -> None:
        old, new = self.state_machine.transition(SystemState.NO_USER)
        print(f"[AppController] state: {old.value} -> {new.value}")
        self.storage.initialize()
        self._bootstrap_user()
        self.device_manager.initialize()
        tick_count = ticks if ticks is not None else int(self.config.get("mock", {}).get("run_ticks", 40))
        tick_interval_ms = int(self.config.get("app", {}).get("tick_interval_ms", 50))
        now_ms = 0
        for _ in range(tick_count):
            now_ms += tick_interval_ms
            events = self.device_manager.poll_events()
            self.data_center.ingest_events(events, now_ms=now_ms)
            profile = None if self.current_user is None or self.current_user["user_type"] == "guest" else self.profile_manager.get_profile(self.current_user["user_id"])
            bound_cp = None
            if profile and profile.get("last_calibration_id"):
                bound_cp = self.storage.get_calibration_profile(profile["last_calibration_id"])
            gate = self.quality_gate.evaluate(self.data_center.get_runtime_snapshot(), self.current_user, profile, bound_cp, self.data_center.get_snapshot().warning_flags, self.data_center.get_snapshot().error_flags)
            self.data_center.apply_quality_gate(gate)
            if debug:
                snapshot = self.data_center.get_runtime_snapshot()
                print(
                    "[mock] "
                    f"t={snapshot['now_ms']} "
                    f"att={snapshot['attention']} age={snapshot['attention_age_ms']} fresh={snapshot['attention_fresh']} "
                    f"gyro_age={snapshot['gyro_age_ms']} fresh={snapshot['gyro_fresh']} "
                    f"q={snapshot['quality']} train={snapshot['training_data_valid']} ctrl={snapshot['control_data_valid']} "
                    f"sqi={snapshot['sqi']} quality_state={snapshot['quality_state']} quality_reasons={snapshot['quality_reasons']} "
                    f"calibration_usable={snapshot['calibration_usable']} formal_training_allowed={snapshot['formal_training_allowed']} "
                    f"signal_reliable={snapshot['signal_reliable']} estimation_allowed={snapshot['estimation_allowed']}"
                )

    def shutdown(self) -> None:
        self.storage.shutdown()
        old, new = self.state_machine.transition(SystemState.SHUTDOWN)
        print(f"[AppController] state: {old.value} -> {new.value}")
