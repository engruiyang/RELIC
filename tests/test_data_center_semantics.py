import unittest
from data.data_center import DataCenter

class T(unittest.TestCase):
    def test_attention_none_invalid(self):
        dc=DataCenter(); now=1000
        dc.ingest_events([{'type':'device_status','device_connected':True,'bridge_alive':True}],now)
        s=dc.tick(now)
        self.assertFalse(s.training_data_valid)
        self.assertNotIn(s.control_state,['STABLE_FOCUS','HIGH_FOCUS'])
    def test_attention_seen_then_valid_possible(self):
        dc=DataCenter(); now=1000
        ev=[{'type':'device_status','device_connected':True,'bridge_alive':True},{'type':'algorithm_frame','algorithm':'attention','data':{'attention':60}},{'type':'algorithm_frame','algorithm':'gyroscope','data':{'focus_x':1,'focus_y':1,'gyro_x':1,'gyro_y':1,'gyro_z':1}}]
        dc.ingest_events(ev,now); s=dc.tick(now)
        self.assertTrue(s.attention_seen_once)
        self.assertTrue(s.training_data_valid)
if __name__=='__main__': unittest.main()
