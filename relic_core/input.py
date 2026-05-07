from .models import InputEvent
class InputManager:
    KEY_MAP={"ENTER":"KeyConfirm","SPACE":"KeyConfirm","ESC":"KeyCancel","P":"KeyPause","R":"KeyRestart","M":"KeyMenu","F12":"DebugToggle"}
    def __init__(self): self._q=[]
    def push_event(self,event:InputEvent)->None: self._q.append(event)
    def poll_events(self)->list[InputEvent]: q=self._q[:]; self._q.clear(); return q
    def clear(self)->None: self._q.clear()
    def make_key_event(self,key:str)->InputEvent:
        k=key.upper(); return InputEvent(event_type=self.KEY_MAP.get(k,key),key=key)
    def make_mouse_click(self,x:float,y:float,button:str='left')->InputEvent:
        return InputEvent(event_type='MouseClick',x=x,y=y,button=button)
