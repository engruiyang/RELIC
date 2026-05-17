from dataclasses import dataclass, field


@dataclass
class RealtimeSnapshot:
    now_ms: int = 0

    attention: int | None = None
    attention_last_update_ms: int | None = None
    attention_age_ms: int | None = None
    attention_fresh: bool = False
    attention_seen_once: bool = False

    gyro_x: float | None = None
    gyro_y: float | None = None
    gyro_z: float | None = None
    gyro_last_update_ms: int | None = None
    gyro_age_ms: int | None = None
    gyro_fresh: bool = False
    gyro_seen_once: bool = False
    focus_seen_once: bool = False

    device_connected: bool = False
    stream_alive: bool = False
    sensor_stream_active: bool = False

    display_data_available: bool = False
    training_data_valid: bool = False
    control_data_valid: bool = False
    recovering: bool = False

    quality: str = "warning"
    quality_reasons: list[str] = field(default_factory=list)
    warning_flags: list[str] = field(default_factory=list)
    error_flags: list[str] = field(default_factory=list)
    sqi: float = 0.0
    quality_state: str = "error"
    calibration_usable: bool = False
    formal_training_allowed: bool = False
    signal_reliable: bool = False
    estimation_allowed: bool = False
    s_eeg: float | None = None
    s_imu: float | None = None
    s_b: float = 0.5
    s_b_source: str = "neutral_default"
    behavior_ready: bool = False
    attention_normalization_method: str | None = None
    motion_energy: float | None = None
    fi_raw: float | None = None
    fi_smoothed: float | None = None
    fi_valid: bool = False
    fi_provisional: bool = True
    fi_confidence: str = "low"
    fi_reasons: list[str] = field(default_factory=list)
    control_state: str = "UNRELIABLE_SIGNAL"
    control_state_reason: str = "estimation_not_allowed"
    control_state_dwell_ms: int = 0

    # compatibility helper for callers that expect grouped gyro
    @property
    def gyro(self) -> tuple[float | None, float | None, float | None]:
        return (self.gyro_x, self.gyro_y, self.gyro_z)
