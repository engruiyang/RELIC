import unittest
from relic_core.coordinates import CoordinateMapper,Rect
from relic_core.models import RealtimeSnapshot
class T(unittest.TestCase):
    def test_map(self):
        m=CoordinateMapper(); c=Rect(0,0,100,100)
        r=m.map_focus_to_canvas(RealtimeSnapshot.from_dict({'focus_x':50,'focus_y':50,'focus_area_x':0,'focus_area_y':0,'focus_area_width':100,'focus_area_height':100}),c)
        self.assertTrue(r['valid']); self.assertEqual(r['game_x'],50)
        bad=m.map_focus_to_canvas(RealtimeSnapshot.from_dict({'focus_x':1}),c); self.assertFalse(bad['valid'])
        out=m.map_focus_to_canvas(RealtimeSnapshot.from_dict({'focus_x':150,'focus_y':-10,'focus_area_x':0,'focus_area_y':0,'focus_area_width':100,'focus_area_height':100}),c)
        self.assertEqual(out['normalized_x'],1.0); self.assertEqual(out['normalized_y'],0.0); self.assertFalse(out['inside_canvas'])
if __name__=='__main__': unittest.main()
