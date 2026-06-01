import subprocess
from pathlib import Path
import json


def test_contract_gate_includes_multi_page_examples() -> None:
    result = subprocess.run(["python", "tools/check_task26_contracts.py"], check=True, capture_output=True, text=True)
    assert "TASK26" in result.stdout


def test_each_formal_page_demo_has_cards() -> None:
    for path in Path("assets/layouts/task26_examples").glob("*_page.desktop_demo.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("cards"), path.name
