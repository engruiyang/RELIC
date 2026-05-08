from game.fake_game_client import FakeGameClient
class GameManager:
    def __init__(self): self.active_game=None
    def load_fake(self)->None: self.active_game=FakeGameClient()
