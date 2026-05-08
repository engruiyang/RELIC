from runtime.runtime_api import RuntimeAPI
class LocalRuntime(RuntimeAPI):
    def tick(self,dt_ms:int)->dict: return {'tick_ms':dt_ms}
