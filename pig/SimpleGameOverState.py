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
    restart = False
    layers = ["__pause__", "__text__"]    

    def enter(self, font_file=None, font_size=None, unpause_keys=[]):
        from pug.all_components import Textbox
        from pig import PigSprite
        from pig.util import get_display_center
        PauseState.enter( self, unpause_keys=unpause_keys)
        backSprite = PigSprite()
        backSprite.set_image('art//block.png')
        backSprite.color = (0, 0, 0, 0.8)
        backSprite.set_layer('__pause__')
        gameOverSprite = PigSprite()
        pressKeySprite = PigSprite()
        textarg = {'text':'GAME OVER', 'hotspot':(0.5, 0.5)}
        if font_file:
            textarg['font_file']=font_file
        if font_size:
            textarg['font_size']=font_size
        text = gameOverSprite.components.add( Textbox( **textarg))
        text.do_set_text() # have to do it manually because we're paused
        textarg['text'] = 'Press Any Key'
        text = pressKeySprite.components.add( Textbox( **textarg))
        text.do_set_text()
        gameOverSprite.position = get_display_center()
        pressKeySprite.position = (gameOverSprite.position[0],
                                   gameOverSprite.position[1] + \
                                   gameOverSprite.image.get_height())
        backSprite.scale = (max(gameOverSprite.image.get_width(),
                                pressKeySprite.image.get_width()) / 2.0, 
                            (gameOverSprite.image.get_height() + \
                            pressKeySprite.image.get_height()) / 2.0)
        backSprite.position = (gameOverSprite.position[0],
                               (gameOverSprite.position[1] + \
                                pressKeySprite.position[1]) / 2.0 )
        gameOverSprite.set_layer('__text__')
        pressKeySprite.set_layer('__text__')
        self.gameOverSprite = gameOverSprite
        self.starttime = time.time()
        self.restart = False
                
    def unpause(self):
        if time.time() >= self.starttime + 1.0:
            self.restart = True
            PauseState.unpause(self)
        
    def exit(self):
        from pig.gamedata import get_gamedata
        PigDirector.paused = False
        PigDirector.game_started = False
        if self.restart:
            gamedata = get_gamedata()
            PigDirector.set_scene( gamedata.start_sceneclass)
        