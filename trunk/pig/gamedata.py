"""gamedata.py 

This module defines a gamedata object meant for global game information and
functionality. To create the gamedata object, call the create_gamedata function in this 
module. 
A good place to set up info in gamedata is in your first scene's
on_project_start method.
"""

import pug

from pig.SimpleGameOverState import SimpleGameOverState
from pig.actions import *
from pig.PigDirector import PigDirector

def simple_game_over( font_file=None, font_size=None):
    """simple_game_over( font_file=None, font_size=None)

font_file: the font_file for the "Game Over" sprite
font_size: the font_size for the "Game Over" sprite

Stop scene and show game over sprite in center. After 2 seconds, pressing any
key will restart the game. 
"""
    scene = PigDirector.scene
    scene.set_state(SimpleGameOverState, font_file=font_size, 
                    font_size=font_size)

class GameDataObject( pug.CallbackObject):
    """GameDataObject: use the create_gamedata method to create this.

Standard methods:
    gameover(*a, **kw): call self._gameover_method( *a, **kw)
Standard attributes:
    gameover_method: method to call via gameover method
    start_sceneclass: class of the first scene that was run
"""
    gameover_method = simple_game_over
    start_sceneclass = None
    def gameover(self, *a, **kw):
        (Delay(0) + CallFunc(self.gameover_method, *a, **kw)).do()
        
GameData = GameDataObject( gname='GameData')
def create_gamedata(**attributes):
    """create_gamedata(**attributes)->GameDataObject
    
attributes: the gamedata object's attributes will be set by these keywords

This function creates a GameDataObject meant to be used globally by means of the
get_gamedata function in this module. This is a convenient place to store
global game data such as score or global game methods like gameover
"""
    global GameData
    GameData.clear_callbacks()
    GameData = GameDataObject( gname='GameData')
    for attr, data in attributes.iteritems():
        setattr(GameData, attr, data)
    return GameData
def get_gamedata():
    return GameData
create_gamedata()
