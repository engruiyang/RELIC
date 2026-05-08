import unittest

from relic_core.bridge_adapter import MockDataBridge


class TestBridgeLifecycle(unittest.TestCase):
    def test_bridge_stopped_connected_false(self):
        b = MockDataBridge()
        b.start()
        self.assertTrue(b.get_snapshot().get("connected"))
        b.stop()
        s = b.get_snapshot()
        self.assertFalse(s.get("connected"))
        self.assertFalse(s.get("bridge_alive"))


if __name__ == "__main__":
    unittest.main()
