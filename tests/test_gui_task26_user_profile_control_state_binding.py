from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding='utf-8')


def test_control_state_exposes_profile_threshold_and_calibration_fields() -> None:
    text = _read('gui/gui_facade.py')
    for token in [
        '"attention_low_threshold": merged_detail.get("attention_low_threshold", "n/a")',
        '"attention_high_threshold": merged_detail.get("attention_high_threshold", "n/a")',
        '"preferred_game_id": merged_detail.get("preferred_game_id", "n/a")',
        '"difficulty_level": merged_detail.get("difficulty_level", "n/a")',
        '"attention_baseline": merged_detail.get("attention_baseline", "")',
        '"gyro_noise_rms": merged_detail.get("gyro_noise_rms", "")',
    ]:
        assert token in text


def test_control_state_uses_baseline_profile_context_not_only_last_action() -> None:
    text = _read('gui/gui_facade.py')
    assert 'def _baseline_user_profile_context' in text
    assert 'baseline_detail = self._baseline_user_profile_context(current_user_id)' in text
    
    assert '_last_user_profile_detail' in text
    assert '_last_user_calibration_detail' in text
    assert 'for src in (baseline_detail,' in text
    assert 'self._last_user_profile_detail' in text
    assert 'self._last_user_calibration_detail' in text



def test_user_layout_payload_is_hydrated_from_control_state_values() -> None:
    text = _read('gui/gui_facade.py')
    assert 'def _hydrate_layout_payload_from_control_state' in text
    assert 'source.startswith("controlStateJson.") or source.startswith("controlState.")' in text
    assert 'payload[f"{prefix}_value"] = str(value)' in text
    assert 'self._hydrate_layout_payload_from_control_state(payload, self.get_control_state())' in text


def test_core_control_user_selection_keeps_gui_override() -> None:
    text = _read('gui/gui_facade.py')
    assert 'self._current_user_override = str(user_id or "")' in text
    assert 'def _current_user_id_for_control_state' in text
    assert 'self._current_user_override = str(user_id)' in text
