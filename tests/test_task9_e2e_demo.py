import json
from pathlib import Path
import subprocess
import sys


def test_task9_e2e_demo_runs(tmp_path):
    db = tmp_path / "e2e.db"
    p = subprocess.run([sys.executable, "-m", "ui_cli.run_task9_e2e_demo", "--db-path", str(db), "--duration-sec", "2"], capture_output=True, text=True, check=True)
    out = json.loads(p.stdout.strip().splitlines()[-1])
    assert out["session_id"]
    assert out["replay_event_count"] > 0
    assert out["platform_report_status"] == "uploaded"
    rp = Path(out["report_path"])
    assert rp.exists()
    content = rp.read_text(encoding="utf-8")
    assert "RELIC 训练会话报告" in content
    assert out["session_id"] in content
