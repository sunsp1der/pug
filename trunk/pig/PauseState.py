from pig.PigState import PigState
from pig.PigDirector import PigDirector

class PauseState(PigState):
    """PauseState( next_state=None, unpause_keys=[]): Pauses the game. 

next_state: state to enter when unpaused. 
unpause_keys: list of keys that cause unpause. [] means any key
"""
    layers = ["__pause__"]
    
    def enter(self, next_state=None, unpause_keys=[]):
        PigDirector.paused = True
        self.next_state=next_state
        self.unpause_keys = unpause_keys
        
    def exit(self):
        PigDirector.paused = False
        
    def unpause(self):
        PigDirector.scene.state = self.next_state
        
    def handle_keydown(self, ev):
        if self.unpause_keys == [] or ev.key in self.unpause_keys:
            self.unpause()

    def handle_keyup(self, ev):
        pass
            
    def handle_mousebuttondown(self, ev):
        pass
    
    def handle_mousebuttonup(self, ev):
        if self.unpause_keys == [] or "MOUSEUP" in self.unpause_keys:
            self.unpause()   