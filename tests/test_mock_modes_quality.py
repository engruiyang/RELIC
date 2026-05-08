import unittest
from device.adapters.mock_adapter import MockAdapter
from data.data_center import DataCenter

class T(unittest.TestCase):
    def run_mode(self,mode,steps=80):
        m=MockAdapter(mode=mode); dc=DataCenter(); now=0
        s=None; seen=[]
        for _ in range(steps):
            now+=100; dc.ingest_events(m.poll(100),now); s=dc.tick(now); seen.extend(s.quality_reasons)
        return s, seen
    def test_missing_start(self):
        s,_=self.run_mode('attention_missing_start',30)
        self.assertFalse(s.attention_seen_once)
        self.assertFalse(s.training_data_valid)
        self.assertTrue(s.fi_provisional)
    def test_short_dropout_warning(self):
        s,_=self.run_mode('attention_short_dropout',70)
        self.assertIn(s.quality,['warning','ok'])
    def test_long_lost_error(self):
        s,_=self.run_mode('attention_long_lost',100)
        self.assertEqual(s.quality,'error')
    def test_focus_jump_reason(self):
        s,seen=self.run_mode('focus_jump',70)
        self.assertIn('focus_jump',seen)
    def test_gyro_spike_reason(self):
        s,seen=self.run_mode('gyro_spike',70)
        self.assertIn('gyro_spike',seen)
    def test_stream_drop(self):
        s,_=self.run_mode('stream_drop',100)
        self.assertFalse(s.stream_alive)
        self.assertFalse(s.training_data_valid)
if __name__=='__main__': unittest.main()
