from relic_core.game_api import BaseGame
from relic_core.models import GameMetrics
class EmptyGame(BaseGame):
    game_id='empty_game'; display_name='Empty Game'
    def __init__(self): super().__init__(); self.tick_count=0; self.input_count=0; self._acc_ms=0
    def start(self): self.context.session_manager.write_game_event('game_start')
    def update(self,dt_ms,snapshot):
        if self.paused: return
        self.tick_count+=1; self._acc_ms+=dt_ms
        if self._acc_ms>=1000:
            self._acc_ms=0; self.context.session_manager.write_game_event('game_tick',snapshot=snapshot,payload={'ticks':self.tick_count})
    def handle_input(self,event):
        if event.event_type in ('MouseClick','CliCommand','KeyPause'):
            self.input_count+=1
            if event.event_type=='KeyPause': self.paused=not self.paused
            self.context.session_manager.write_game_event('input_event',payload={'type':event.event_type})
    def end(self,reason='normal'): self.context.session_manager.write_game_event('game_end',payload={'reason':reason})
    def cleanup(self): super().cleanup()
    def get_metrics(self): return GameMetrics(extra={'ticks':self.tick_count,'inputs':self.input_count})
