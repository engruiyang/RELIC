import unittest
from relic_core.quality import QualityManager
from relic_core.focus import FocusModel
from relic_core.models import RealtimeSnapshot
class T(unittest.TestCase):
    def test_quality_and_focus(self):
        qm=QualityManager(); fm=FocusModel()
        q=qm.evaluate({'connected':False}); self.assertEqual(q.status,'error')
        q2=qm.evaluate({'connected':True,'attention_valid':True,'attention_age_ms':5000,'gyro_valid':True,'gyro_age_ms':0}); self.assertLess(q2.sqi,1)
        q3=qm.evaluate({'connected':True,'attention_valid':True,'attention_age_ms':0,'gyro_valid':True,'gyro_age_ms':1000}); self.assertLess(q3.sqi,1)
        f=fm.compute(RealtimeSnapshot.from_dict({'connected':True,'attention_value':100,'gyro_valid':True,'gyro_age_ms':0}),quality=q3); self.assertAlmostEqual(f.s_eeg,1.0)
        self.assertTrue(0<=f.fi<=100)
        low=qm.evaluate({'connected':False}); f2=fm.compute({'connected':True,'attention_value':50,'gyro_valid':False},quality=low); self.assertFalse(f2.valid)
if __name__=='__main__': unittest.main()
