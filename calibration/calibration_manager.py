from calibration.calibration_profile import CalibrationProfile
class CalibrationManager:
    def get_profile(self,user_id:str|None)->CalibrationProfile: return CalibrationProfile(profile_id=user_id or 'default',ready=False)
