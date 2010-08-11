from pig.PigState import PigState
from pig.PigDirector import PigDirector

class PauseState(PigState):
    layers = ["__pause__"]
    unpause_keys = []
    def enter(self, nextState=None):
        PigDirector.paused = True
        self.nextState=nextState
        
    def exit(self):
        PigDirector.paused = False
        
    def unpause(self):
        PigDirector.scene.state =  self.nextState
        
    def handle_keydown(self, ev):
        if self.unpause_keys ==[] or ev.key in self.unpause_keys:
            self.unpause()

    def handle_keyup(self, ev):
        if self.unpause_keys ==[] or ev.key in self.unpause_keys:
            self.unpause()
            
    def handle_mousebuttondown(self, event):
        pass
    
    def handle_mousebuttonup(self, event):
        pass    