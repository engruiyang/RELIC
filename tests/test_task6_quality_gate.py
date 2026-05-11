from core.quality_gate import QualityGate
from data.data_center import DataCenter


def _base_snapshot():
    return {"baseline_confidence": "high"}


def test_no_user_formal_training_disabled():
    q = QualityGate().evaluate(_base_snapshot(), None, None, None, [], [])
    assert q["formal_training_allowed"] is False
    assert "no_user" in q["quality_reasons"]


def test_no_calibration_formal_training_disabled():
    profile = {"user_id": "TEST", "last_calibration_id": None}
    q = QualityGate().evaluate(_base_snapshot(), {"user_id": "TEST"}, profile, None, [], [])
    assert q["formal_training_allowed"] is False
    assert "no_calibration" in q["quality_reasons"]


def test_binding_inconsistent_not_usable():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_b", "valid": True, "device_id": "ipc_device"}
    q = QualityGate().evaluate(_base_snapshot(), {"user_id": "TEST"}, profile, cp, [], [])
    assert q["calibration_usable"] is False
    assert "calibration_binding_inconsistent" in q["quality_reasons"]


def test_mock_calibration_usable_but_not_formal():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "mock_device", "attention_std": 5}
    q = QualityGate().evaluate(_base_snapshot(), {"user_id": "TEST"}, profile, cp, [], [])
    assert q["calibration_usable"] is True
    assert q["formal_training_allowed"] is False


def test_ipc_valid_calibration_usable():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "ipc_device", "attention_std": 5}
    q = QualityGate().evaluate(_base_snapshot(), {"user_id": "TEST"}, profile, cp, [], [])
    assert q["calibration_usable"] is True


def test_attention_lost_blocks_estimation():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "ipc_device", "attention_std": 5}
    q = QualityGate().evaluate(_base_snapshot(), {"user_id": "TEST"}, profile, cp, [], ["attention_lost"])
    assert q["quality_state"] == "error"
    assert q["estimation_allowed"] is False
    assert q["formal_training_allowed"] is False


def test_gyro_lost_blocks_estimation():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "ipc_device", "attention_std": 5}
    q = QualityGate().evaluate(_base_snapshot(), {"user_id": "TEST"}, profile, cp, [], ["gyro_lost"])
    assert q["quality_state"] == "error"
    assert q["estimation_allowed"] is False
    assert q["formal_training_allowed"] is False


def test_attention_missing_blocks_estimation_and_reliability():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "ipc_device", "attention_std": 5}
    q = QualityGate().evaluate({"attention_fresh": False, "gyro_fresh": True, "baseline_confidence": "high"}, {"user_id": "TEST"}, profile, cp, ["attention_missing"], [])
    assert q["quality_state"] == "warning"
    assert q["signal_reliable"] is False
    assert q["estimation_allowed"] is False
    assert q["formal_training_allowed"] is False


def test_gyro_missing_blocks_estimation_and_reliability():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "ipc_device", "attention_std": 5}
    q = QualityGate().evaluate({"attention_fresh": True, "gyro_fresh": False, "baseline_confidence": "high"}, {"user_id": "TEST"}, profile, cp, ["gyro_missing"], [])
    assert q["quality_state"] == "warning"
    assert q["signal_reliable"] is False
    assert q["estimation_allowed"] is False
    assert q["formal_training_allowed"] is False


def test_fresh_signals_with_usable_calibration_allow_estimation():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "ipc_device", "attention_std": 5}
    q = QualityGate().evaluate({"attention_fresh": True, "gyro_fresh": True, "baseline_confidence": "high"}, {"user_id": "TEST"}, profile, cp, [], [])
    assert q["signal_reliable"] is True
    assert q["estimation_allowed"] is True


def test_attention_std_zero_adds_reason():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "ipc_device", "attention_std": 0}
    q = QualityGate().evaluate(_base_snapshot(), {"user_id": "TEST"}, profile, cp, [], [])
    assert "attention_std_zero_fallback_required" in q["quality_reasons"]
    assert q["estimation_allowed"] is True


def test_low_baseline_confidence_warning():
    profile = {"user_id": "TEST", "last_calibration_id": "cal_a"}
    cp = {"calibration_id": "cal_a", "valid": True, "device_id": "ipc_device", "attention_std": 5}
    q = QualityGate().evaluate({"baseline_confidence": "low"}, {"user_id": "TEST"}, profile, cp, [], [])
    assert q["quality_state"] == "warning"


def test_runtime_snapshot_quality_fields_serializable():
    dc = DataCenter()
    dc.apply_quality_gate({"sqi": 0.9, "quality_state": "ok", "quality_reasons": [], "calibration_usable": True, "formal_training_allowed": True, "signal_reliable": True, "estimation_allowed": True})
    s = dc.get_runtime_snapshot()
    assert "sqi" in s and "quality_state" in s and "estimation_allowed" in s
