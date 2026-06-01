import subprocess


def test_contract_gate_default_passes() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py"], check=True, capture_output=True, text=True)
    assert "TASK26" in result.stdout and "ok" in result.stdout


def test_contract_gate_strict_passes() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py", "--strict"], check=True, capture_output=True, text=True)
    assert "TASK26" in result.stdout and "strict ok" in result.stdout


def test_contract_gate_strict_show_diff_passes() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py", "--strict", "--show-diff"], check=True, capture_output=True, text=True)
    assert "TASK26 injection contract diff" in result.stdout
    assert "strict ok" in result.stdout
