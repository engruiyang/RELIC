from device.adapters.mock_adapter import MockAdapter

class DeviceManager:
    def __init__(self): self.adapter=MockAdapter()
    def initialize(self)->None: ...
    def status(self)->dict: return {'connected':True}
    def poll_events(self,dt_ms:int)->list[dict]:
        return self.adapter.poll(dt_ms)
