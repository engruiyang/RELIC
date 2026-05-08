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
        self.assertEqual(s.control_state,'NO_SIGNAL')
    def test_partial_stale_no_strong_state(self):
        s,seen=self.run_mode('partial_stale',80)
        self.assertIn('gyro_stale',seen)
        self.assertIn(s.quality,['warning','ok'])
        self.assertNotIn(s.control_state,['FATIGUED','HIGH_FOCUS','STABLE_FOCUS'])
    def test_reconnect_recovery_semantics(self):
        m=MockAdapter(mode='reconnect_recovery'); dc=DataCenter(); now=0
        seen_stream_inactive=False; seen_recovered_stale=False; seen_zero_attention=False
        for _ in range(130):
            now+=100
            dc.ingest_events(m.poll(100),now)
            s=dc.tick(now)
            self.assertIsInstance(s.attention_seen_once,bool)
            self.assertIsInstance(s.focus_seen_once,bool)
            self.assertIsInstance(s.gyro_seen_once,bool)
            self.assertIsInstance(s.warning_flags,list)
            self.assertIsInstance(s.error_flags,list)
            self.assertIsInstance(s.fi_provisional,bool)
            if not s.stream_alive:
                seen_stream_inactive=True
                self.assertFalse(s.training_data_valid)
                self.assertFalse(s.fi_valid)
                self.assertEqual(s.control_state,'NO_SIGNAL')
            if seen_stream_inactive and s.stream_alive and ('attention_stale' in s.quality_reasons or s.recovering):
                seen_recovered_stale=True
                self.assertFalse(s.control_data_valid)
                self.assertFalse(s.fi_valid)
                self.assertNotIn(s.control_state,['STABLE_FOCUS','HIGH_FOCUS'])
            if s.attention == 0 and s.stream_alive:
                seen_zero_attention=True
                self.assertNotEqual(s.control_state,'FATIGUED')
        self.assertTrue(seen_stream_inactive)
        self.assertTrue(seen_recovered_stale)
        self.assertTrue(seen_zero_attention)
if __name__=='__main__': unittest.main()
