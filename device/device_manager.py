from device.adapters import MockAdapter


class DeviceManager:
    def __init__(self, mock_mode: str = "normal") -> None:
        self._adapter = MockAdapter(mode=mock_mode)

    def initialize(self) -> None:
        self._adapter.connect()

    def status(self) -> dict:
        return {"connected": self._adapter.connected}

    def poll_events(self) -> list[dict]:
        return self._adapter.read()
