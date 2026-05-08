from ui_cli.run_core_debug import run_debug_loop


def test_cli_uses_data_center_snapshot_output(capsys):
    run_debug_loop(mode="mock", host="127.0.0.1", port=8000, ticks=2, interval=0.0)
    out = capsys.readouterr().out
    assert "attention_age_ms=" in out
    assert "training_data_valid=" in out
    assert "quality=" in out
