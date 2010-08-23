import time

from pig.PauseState import PauseState
from pig.PigDirector import PigDirector
from pig.actions import Delay, CallFunc

class SimpleGameOverState(PauseState):
    """SimpleGameOverState( font_file=None, font_size=None, unpause_keys=[])
    
Pause game, display "GAME OVER". When unpaused, return to starting scene of 
project.
font_file: "GAME OVER" font
font_size: "GAME OVER" font size
unpause_keys: list of keys that cause unpause. [] means any key
"""
    def enter(self, font_file=None, font_size=None, unpause_keys=[]):
        from pug.all_components import Textbox
        from pig import PigSprite
        from pig.util import get_display_center
        PauseState.enter( self, unpause_keys=unpause_keys)
        gameOverSprite = PigSprite()
        textarg = {'text':'GAME OVER'}
        if font_file:
            textarg['font_file']=font_file
        if font_size:
            textarg['font_size']=font_size
        text = gameOverSprite.components.add( Textbox( **textarg))
        text.do_set_text() # have to do it manually because we're paused
        gameOverSprite.position = get_display_center()
        gameOverSprite.set_layer('__pause__')
        self.gameOverSprite = gameOverSprite
        self.starttime = time.time()
                
    def unpause(self):
        if time.time() >= self.starttime + 1.5:
            PauseState.unpause(self)
        
    def exit(self):
        from pig.gamedata import get_gamedata
        PigDirector.paused = False
        gamedata = get_gamedata()
        PigDirector.project_started = False
        PigDirector.set_scene( gamedata.start_sceneclass)
        