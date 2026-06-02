import json
from pathlib import Path
import subprocess


def test_training_contract_summary_shape_and_guards() -> None:
    data = json.loads(Path("assets/layouts/task26_examples/training_page.desktop_demo.json").read_text(encoding="utf-8"))
    cards = {c.get("id") for c in data.get("cards", [])}
    assert {"game_canvas_card", "game_hud_card", "training_control_card", "difficulty_control_card"} <= cards
    actions = {w.get("action_id") for c in data.get("cards", []) for w in c.get("widgets", [])}
    assert {"session.start", "session.stop", "live.safe_stop", "game.difficulty"} <= actions


def test_training_slots_are_supported_in_current_formal_training_page() -> None:
    data = json.loads(Path("assets/layouts/task26_examples/training_page.desktop_demo.json").read_text(encoding="utf-8"))
    assert len(data.get("cards", [])) == 4
    assert data["cards"][0]["id"] == "game_canvas_card"


def test_task26_contract_gate_strict_includes_training() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py", "--strict"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "strict ok" in result.stdout
