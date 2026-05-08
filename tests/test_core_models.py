import unittest
from relic_core.models import RealtimeSnapshot,QualityResult,FocusResult,InputEvent
class T(unittest.TestCase):
    def test_snapshot(self):
        s=RealtimeSnapshot.from_dict({'connected':True}); self.assertTrue(s.connected); self.assertIsNone(s.focus_x); self.assertIn('connected',s.to_dict())
    def test_clamp(self):
        self.assertEqual(QualityResult(2,'ok').sqi,1.0); self.assertEqual(FocusResult(120,1,1,1).fi,100.0)
    def test_input(self):
        e=InputEvent('MouseClick',x=1,y=2); self.assertEqual(e.event_type,'MouseClick')
if __name__=='__main__': unittest.main()
