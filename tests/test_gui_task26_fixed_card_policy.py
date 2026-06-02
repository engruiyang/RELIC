import json
from pathlib import Path
import subprocess


def _load(name: str) -> dict:
    return json.loads(Path("assets/layouts/task26_examples", name).read_text(encoding="utf-8"))


def test_fixed_or_locked_cards_are_not_removable_when_policy_is_present() -> None:
    for path in Path("assets/layouts/task26_examples").glob("*_page.desktop_demo.json"):
        page = json.loads(path.read_text(encoding="utf-8"))
        for card in page.get("cards", []):
            policy = card.get("card_policy") if isinstance(card.get("card_policy"), dict) else {}
            if card.get("required") or card.get("locked") or policy.get("fixed") or policy.get("locked"):
                assert policy.get("allow_remove") is not True


def test_task26_contract_gate_runs_fixed_card_policy() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py", "--strict"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + result.stdout
