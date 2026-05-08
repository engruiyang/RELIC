import unittest
from relic_core.runtime import AppCore

class FakeBridge:
    def __init__(self): self.running=False; self.snap={'connected':True,'bridge_alive':True,'attention_valid':True,'gyro_valid':True,'attention_age_ms':100,'gyro_age_ms':100,'last_algorithm_msg_age_ms':100}
    def start(self): self.running=True
    def stop(self): self.running=False
    def close(self): self.running=False
    def is_alive(self): return self.running
    def get_snapshot(self): return dict(self.snap)

class T(unittest.TestCase):
    def test_fresh_valid(self):
        b=FakeBridge(); c=AppCore(b); c.start(); c.start_game('empty_game'); out=c.tick(50); self.assertTrue(out['training_data_valid'])
    def test_inactive_nosignal(self):
        b=FakeBridge(); c=AppCore(b); c.start(); c.start_game('empty_game'); b.snap.update({'attention_age_ms':9000,'gyro_age_ms':5000,'last_algorithm_msg_age_ms':7000}); out=c.tick(50)
        self.assertFalse(out['sensor_stream_active']); self.assertEqual(out['focus_state'],'NO_SIGNAL')
if __name__=='__main__': unittest.main()
