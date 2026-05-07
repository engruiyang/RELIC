import unittest

from relic_core.difficulty import StateMachine
from relic_core.focus import FocusModel
from relic_core.quality import QualityManager


class TestQualityFocus(unittest.TestCase):
    def test_bridge_disconnected_error(self):
        qm = QualityManager()
        q = qm.evaluate({"connected": False})
        self.assertEqual(q.status, "error")
        self.assertIn("bridge_disconnected", q.reasons)

    def test_attention_stale_penalty(self):
        qm = QualityManager(attention_stale_ms=3000)
        q = qm.evaluate({"connected": True, "attention_valid": True, "attention_age_ms": 5001, "gyro_valid": True, "gyro_age_ms": 10})
        self.assertLess(q.sqi, 1.0)
        self.assertIn("attention_stale", q.reasons)

    def test_gyro_stale_penalty(self):
        qm = QualityManager(gyro_stale_ms=500)
        q = qm.evaluate({"connected": True, "attention_valid": True, "attention_age_ms": 100, "gyro_valid": True, "gyro_age_ms": 1200})
        self.assertLess(q.sqi, 1.0)
        self.assertIn("gyro_stale", q.reasons)

    def test_state_nosignal_when_bridge_down(self):
        qm = QualityManager()
        fm = FocusModel()
        sm = StateMachine()
        q = qm.evaluate({"connected": False})
        f = fm.compute({"connected": False, "attention_value": 50, "gyro_valid": False}, quality=q)
        st = sm.update(f, q)
        self.assertEqual(st, "NO_SIGNAL")


if __name__ == "__main__":
    unittest.main()
