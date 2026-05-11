from core.focus_estimator import FocusEstimator
from core.control_state_estimator import ControlStateEstimator


def _profile():
    return {"attention_low_threshold": 40, "attention_high_threshold": 70}


def _cal(std=5.0, noise=1.0):
    return {"attention_baseline": 55, "attention_std": std, "gyro_bias_x": 0.0, "gyro_bias_y": 0.0, "gyro_bias_z": 0.0, "gyro_noise_rms": noise}


def _snap():
    return {"attention": 65, "attention_fresh": True, "gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_fresh": True, "estimation_allowed": True, "quality_state": "ok"}


def test_estimation_not_allowed_invalid():
    f = FocusEstimator()
    r = f.estimate({**_snap(), "estimation_allowed": False}, _profile(), _cal())
    c = ControlStateEstimator().evaluate({"estimation_allowed": False, "quality_state": "ok"}, r)
    assert r["fi_valid"] is False
    assert c["control_state"] == "UNRELIABLE_SIGNAL"


def test_attention_std_zero_fallback():
    f = FocusEstimator()
    r = f.estimate(_snap(), _profile(), _cal(std=0.0))
    assert "attention_std_zero_fallback" in r["fi_reasons"]
    assert r["attention_normalization_method"] in {"profile_threshold_fallback", "baseline_window_fallback"}


def test_attention_std_positive_zscore_and_bounds():
    f = FocusEstimator()
    r = f.estimate(_snap(), _profile(), _cal(std=5.0))
    assert r["attention_normalization_method"] == "z_score"
    assert 0.0 <= r["s_eeg"] <= 1.0


def test_gyro_noise_zero_fallback():
    f = FocusEstimator()
    r = f.estimate(_snap(), _profile(), _cal(noise=0.0))
    assert 0.0 <= r["s_imu"] <= 1.0
    assert "gyro_noise_zero_fallback" in r["fi_reasons"]


def test_behavior_default_source():
    f = FocusEstimator()
    r = f.estimate(_snap(), _profile(), _cal())
    assert r["s_b"] == 0.5
    assert r["s_b_source"] == "neutral_default"
    assert "behavior_score_default" in r["fi_reasons"]


def test_valid_fi_range():
    f = FocusEstimator()
    r = f.estimate(_snap(), _profile(), _cal())
    assert r["fi_valid"] is True
    assert 0 <= r["fi_raw"] <= 100
    assert 0 <= r["fi_smoothed"] <= 100


def test_high_fi_requires_two_windows():
    c = ControlStateEstimator()
    fi = {"fi_valid": True, "fi_confidence": "high", "fi_smoothed": 85, "s_imu": 0.9}
    s = {"estimation_allowed": True, "quality_state": "ok"}
    one = c.evaluate(s, fi)
    two = c.evaluate(s, fi)
    assert one["control_state"] != "HIGH_FOCUS"
    assert two["control_state"] == "HIGH_FOCUS"


def test_medium_and_low_states():
    c = ControlStateEstimator()
    s = {"estimation_allowed": True, "quality_state": "ok"}
    a = c.evaluate(s, {"fi_valid": True, "fi_confidence": "high", "fi_smoothed": 70, "s_imu": 0.8})
    b = c.evaluate(s, {"fi_valid": True, "fi_confidence": "high", "fi_smoothed": 45, "s_imu": 0.8})
    assert a["control_state"] == "STABLE_FOCUS"
    assert b["control_state"] == "DISTRACTED"


def test_warning_forces_low_confidence():
    c = ControlStateEstimator()
    s = {"estimation_allowed": True, "quality_state": "warning"}
    r = c.evaluate(s, {"fi_valid": True, "fi_confidence": "high", "fi_smoothed": 90, "s_imu": 0.9})
    assert r["control_state"] == "LOW_CONFIDENCE"
