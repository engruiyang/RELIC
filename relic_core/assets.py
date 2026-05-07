from pathlib import Path
import json
from typing import Any
DEFAULT_MANIFEST={"images.logo":"images/icons/logo.png","images.main_background":"images/backgrounds/main.png","images.button.normal":"images/buttons/button_normal.png","images.button.hover":"images/buttons/button_hover.png","sounds.click":"sounds/click.wav","fonts.main":"fonts/main.ttf"}
DEFAULT_THEME={"name":"default","font_family":"Microsoft YaHei UI","colors":{"background":"#10131A","panel":"#1B2130","primary":"#70E0FF","secondary":"#8B7CFF","warning":"#FFD166","danger":"#FF5C7A","text":"#F5F7FA","muted_text":"#A7B0C0"},"sizes":{"window_width":1280,"window_height":720,"top_bar_height":72,"bottom_bar_height":48}}
class AssetManager:
    def __init__(self,root:Path|str='.'):
        self.root=Path(root); self.assets_dir=self.root/'assets'; self.mf=self.assets_dir/'manifest.json'; self.tf=self.assets_dir/'themes/default/theme.json'; self._ensure(); self.manifest=json.loads(self.mf.read_text(encoding='utf-8')); self.theme=json.loads(self.tf.read_text(encoding='utf-8'))
    def _ensure(self):
        self.mf.parent.mkdir(parents=True,exist_ok=True); self.tf.parent.mkdir(parents=True,exist_ok=True)
        if not self.mf.exists(): self.mf.write_text(json.dumps(DEFAULT_MANIFEST,ensure_ascii=False,indent=2),encoding='utf-8')
        if not self.tf.exists(): self.tf.write_text(json.dumps(DEFAULT_THEME,ensure_ascii=False,indent=2),encoding='utf-8')
    def get_theme(self)->dict: return self.theme
    def get_color(self,name:str,default:str|None=None)->str|None: return self.theme.get('colors',{}).get(name,default)
    def get_size(self,name:str,default:Any=None)->Any: return self.theme.get('sizes',{}).get(name,default)
    def resolve_path(self,relative_path:str)->Path: return self.assets_dir/relative_path
    def get_asset_path(self,key:str):
        p=self.manifest.get(key); return self.resolve_path(p) if p else None
    def asset_exists(self,key:str)->bool:
        p=self.get_asset_path(key); return bool(p and p.exists())
