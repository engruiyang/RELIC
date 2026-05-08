class UserManager:
    def __init__(self): self.current_user_id=None
    def has_user(self)->bool: return self.current_user_id is not None
