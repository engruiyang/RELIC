import unittest
from copy import deepcopy
from device.adapters.mock_adapter import MockAdapter
from data.data_center import DataCenter

class T(unittest.TestCase):
    def run_mode(self,mode,steps=80):
        m=MockAdapter(mode=mode); dc=DataCenter(); now=0
        snaps=[]
        for _ in range(steps):
            now+=100; dc.ingest_events(m.poll(100),now); snaps.append(deepcopy(dc.tick(now).to_dict()))
        return snaps

    def test_normal_eventually_valid(self):
        snaps=self.run_mode('normal',120)
        self.assertTrue(any(s['training_data_valid'] for s in snaps))
        self.assertTrue(any(s['control_data_valid'] for s in snaps))

    def test_missing_start(self):
        snaps=self.run_mode('attention_missing_start',30)
        s=snaps[-1]
        self.assertIsNone(s['attention'])
        self.assertFalse(s['attention_seen_once'])
        self.assertFalse(s['training_data_valid'])
        self.assertFalse(s['control_data_valid'])
        self.assertEqual(s['quality'],'warning')
        self.assertIn('attention_missing',s['quality_reasons'])

    def test_short_dropout_warning(self):
        snaps=self.run_mode('attention_short_dropout',70)
        self.assertTrue(any('attention_stale' in s['warning_flags'] for s in snaps))
        self.assertTrue(any(not s['control_data_valid'] for s in snaps if 'attention_stale' in s['warning_flags']))

    def test_long_lost_error(self):
        snaps=self.run_mode('attention_long_lost',100)
        s=snaps[-1]
        self.assertIn('attention_lost',s['error_flags'])
        self.assertEqual(s['quality'],'error')
        self.assertFalse(s['training_data_valid'])
        self.assertFalse(s['control_data_valid'])

    def test_gyro_short_dropout_warning(self):
        snaps=self.run_mode('gyro_short_dropout',80)
        self.assertTrue(any('gyro_stale' in s['warning_flags'] for s in snaps))
        for s in snaps:
            if 'gyro_stale' in s['warning_flags']:
                self.assertFalse(s['control_data_valid'])
                self.assertNotEqual(s['quality'],'error')

    def test_stream_drop(self):
        snaps=self.run_mode('stream_drop',100)
        s=snaps[-1]
        self.assertFalse(s['stream_alive'])
        self.assertFalse(s['sensor_stream_active'])
        self.assertFalse(s['training_data_valid'])
        self.assertFalse(s['control_data_valid'])
        self.assertIn('stream_inactive',s['quality_reasons'])

if __name__=='__main__': unittest.main()
