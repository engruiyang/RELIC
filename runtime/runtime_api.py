from abc import ABC, abstractmethod
class RuntimeAPI(ABC):
    @abstractmethod
    def tick(self,dt_ms:int)->dict: ...
