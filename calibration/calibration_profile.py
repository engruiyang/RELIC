from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class CalibrationProfile:
    calibration_id: str
    user_id: str
    device_id: str
    created_at: str
    calibration_type: str
    attention_baseline: float | None
    attention_std: float | None
    attention_valid_sample_ratio: float
    gyro_bias_x: float | None
    gyro_bias_y: float | None
    gyro_bias_z: float | None
    gyro_noise_x: float | None
    gyro_noise_y: float | None
    gyro_noise_z: float | None
    gyro_noise_rms: float | None
    gyro_stability_score: float
    signal_quality_baseline: float
    valid: bool
    failure_reason: str | None
    non_persistent: bool = False

    def to_dict(self) -> dict:
        return asdict(self)
