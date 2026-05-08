from pathlib import Path
import json

def load_config(path:str='config/default_config.json')->dict:
    p=Path(path)
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
