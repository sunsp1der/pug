import pug

from pig.actions import *
from pig.PigDirector import PigDirector

def simple_game_over():
    "Stop scene and show game over sprite in center"
    (Delay(0) + \
     CallFunc(do_simple_game_over)).do()
def do_simple_game_over():
    "Do the actual work of simple_game_over"
    scene = PigDirector.scene

class GameDataObject( pug.CallbackObject):
    _gameover_method = simple_game_over
    def set_gameover_method(self, method):
        self._gameover_method = method
    def gameover(self):
        self._gameover_method()
        
GameData = GameDataObject( gname='GameData')
def create_gamedata(**kw):
    global GameData
    GameData.clear_callbacks()
    GameData = pug.CallbackObject( gname='GameData')
    for attr, data in kw.iteritems():
        setattr(GameData, attr, data)
def get_gamedata():
    return GameData
create_gamedata()
