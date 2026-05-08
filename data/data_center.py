from data.realtime_snapshot import RealtimeSnapshot

class DataCenter:
    def __init__(self): self._snapshot=RealtimeSnapshot()
    def get_snapshot(self)->RealtimeSnapshot: return self._snapshot
    def set_snapshot(self,snapshot:RealtimeSnapshot)->None: self._snapshot=snapshot
