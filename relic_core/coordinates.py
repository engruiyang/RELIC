from dataclasses import dataclass
from .models import RealtimeSnapshot
@dataclass
class Rect: x:float; y:float; width:float; height:float
class CoordinateMapper:
    def map_focus_to_canvas(self,snapshot:RealtimeSnapshot,canvas:Rect)->dict:
        req=[snapshot.focus_x,snapshot.focus_y,snapshot.focus_area_x,snapshot.focus_area_y,snapshot.focus_area_width,snapshot.focus_area_height]
        if any(v is None for v in req) or snapshot.focus_area_width==0 or snapshot.focus_area_height==0:
            return {"game_x":None,"game_y":None,"normalized_x":None,"normalized_y":None,"inside_canvas":False,"valid":False,"reason":"missing_focus_or_area"}
        nx_raw=(snapshot.focus_x-snapshot.focus_area_x)/snapshot.focus_area_width
        ny_raw=(snapshot.focus_y-snapshot.focus_area_y)/snapshot.focus_area_height
        nx=max(0.0,min(1.0,nx_raw)); ny=max(0.0,min(1.0,ny_raw))
        return {"game_x":canvas.x+nx*canvas.width,"game_y":canvas.y+ny*canvas.height,"normalized_x":nx,"normalized_y":ny,"inside_canvas":0<=nx_raw<=1 and 0<=ny_raw<=1,"valid":True,"reason":None}
