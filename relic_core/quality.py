from .models import QualityResult, RealtimeSnapshot


class QualityManager:
    def __init__(self, attention_stale_ms: int = 3000, gyro_stale_ms: int = 500, attention_zero_warning_ms: int = 10000):
        self.attention_stale_ms = attention_stale_ms
        self.gyro_stale_ms = gyro_stale_ms
        self.attention_zero_warning_ms = attention_zero_warning_ms

    def evaluate(self, snapshot):
        s = snapshot if isinstance(snapshot, RealtimeSnapshot) else RealtimeSnapshot.from_dict(snapshot)
        if not s.connected:
            return QualityResult(0.0, "error", ["bridge_disconnected"])

        sqi = 1.0
        reasons: list[str] = []

        if not s.attention_valid:
            sqi -= 0.25
            reasons.append("attention_invalid")
        if s.attention_age_ms is None or s.attention_age_ms > self.attention_stale_ms:
            sqi -= 0.20
            reasons.append("attention_stale")

        if not s.gyro_valid:
            sqi -= 0.25
            reasons.append("gyro_invalid")
        if s.gyro_age_ms is None or s.gyro_age_ms > self.gyro_stale_ms:
            sqi -= 0.20
            reasons.append("gyro_stale")

        if s.attention_value == 0:
            sqi -= 0.1
            reasons.append("attention_zero")

        status = "ok" if sqi >= 0.8 else ("warning" if sqi >= 0.4 else "error")
        return QualityResult(sqi, status, reasons)
