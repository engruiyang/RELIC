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

    device_connected: bool = False
    stream_alive: bool = False
    sensor_stream_active: bool = False

    display_data_available: bool = False
    training_data_valid: bool = False
    control_data_valid: bool = False

    quality: str = "warning"
    quality_reasons: list[str] = field(default_factory=list)
    warning_flags: list[str] = field(default_factory=list)
    error_flags: list[str] = field(default_factory=list)

    # compatibility helper for callers that expect grouped gyro
    @property
    def gyro(self) -> tuple[float | None, float | None, float | None]:
        return (self.gyro_x, self.gyro_y, self.gyro_z)
