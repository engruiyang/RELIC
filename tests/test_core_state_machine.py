import unittest
from relic_core.difficulty import StateMachine
from relic_core.models import FocusResult, QualityResult

class T(unittest.TestCase):
    def test_quality_error(self):
        sm=StateMachine(); st=sm.update(FocusResult(70,0.7,0.7,0.5),QualityResult(0.2,'error'))
        self.assertEqual(st,'NO_SIGNAL')
    def test_training_invalid(self):
        sm=StateMachine(); st=sm.update(FocusResult(70,0.7,0.7,0.5),QualityResult(0.9,'ok'),training_data_valid=False)
        self.assertEqual(st,'NO_SIGNAL')
    def test_stream_inactive(self):
        sm=StateMachine(); st=sm.update(FocusResult(70,0.7,0.7,0.5),QualityResult(0.9,'ok'),training_data_valid=True,stream_state='STREAM_INACTIVE')
        self.assertEqual(st,'NO_SIGNAL')
    def test_normal_mapping(self):
        sm=StateMachine(); self.assertEqual(sm.update(FocusResult(70,0.7,0.7,0.5),QualityResult(0.9,'ok'),training_data_valid=True,stream_state='ACTIVE'),'STABLE_FOCUS')
        self.assertEqual(sm.update(FocusResult(30,0.3,0.3,0.3),QualityResult(0.9,'ok'),training_data_valid=True,stream_state='ACTIVE'),'FATIGUED')
if __name__=='__main__': unittest.main()
