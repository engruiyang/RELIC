import unittest
from relic_core.quality import QualityManager

class TestQualityManager(unittest.TestCase):
    def setUp(self): self.qm=QualityManager()
    def test_ok_fresh(self):
        q=self.qm.evaluate({'bridge_connected':True,'bridge_alive':True,'connected':True,'attention_age_ms':200,'gyro_age_ms':100,'last_algorithm_msg_age_ms':500,'attention_valid':True,'gyro_valid':True})
        self.assertEqual(q.status,'ok')
    def test_warning_gyro_stale(self):
        q=self.qm.evaluate({'bridge_connected':True,'bridge_alive':True,'connected':True,'attention_age_ms':200,'gyro_age_ms':900,'last_algorithm_msg_age_ms':1000,'attention_valid':True,'gyro_valid':True})
        self.assertEqual(q.status,'warning'); self.assertIn('gyro_stale',q.reasons)
    def test_warning_attention_stale(self):
        q=self.qm.evaluate({'bridge_connected':True,'bridge_alive':True,'connected':True,'attention_age_ms':3500,'gyro_age_ms':100,'last_algorithm_msg_age_ms':1000,'attention_valid':True,'gyro_valid':True})
        self.assertEqual(q.status,'warning'); self.assertIn('attention_stale',q.reasons)
    def test_error_severe_both_stale(self):
        q=self.qm.evaluate({'bridge_connected':True,'bridge_alive':True,'connected':True,'attention_age_ms':9000,'gyro_age_ms':5000,'last_algorithm_msg_age_ms':2000,'attention_valid':True,'gyro_valid':True})
        self.assertEqual(q.status,'error')
    def test_error_algorithm_stale(self):
        q=self.qm.evaluate({'bridge_connected':True,'bridge_alive':True,'connected':True,'attention_age_ms':100,'gyro_age_ms':100,'last_algorithm_msg_age_ms':6000,'attention_valid':True,'gyro_valid':True})
        self.assertEqual(q.status,'error'); self.assertIn('algorithm_stream_stale',q.reasons)
    def test_bridge_disconnected(self):
        self.assertEqual(self.qm.evaluate({'bridge_connected':False,'bridge_alive':True}).status,'error')
    def test_bridge_dead(self):
        q=self.qm.evaluate({'bridge_connected':True,'bridge_alive':False}); self.assertEqual(q.status,'error'); self.assertIn('bridge_dead',q.reasons)
    def test_initial_waiting(self):
        q=self.qm.evaluate({'bridge_connected':True,'bridge_alive':True,'attention_age_ms':100,'gyro_age_ms':100,'last_algorithm_msg_age_ms':None})
        self.assertIn(q.status,('warning','waiting')); self.assertIn('initial_waiting',q.reasons)

if __name__=='__main__': unittest.main()
