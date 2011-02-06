from Opioid2D.public.Node import Node
from Opioid2D import Delay, CallFunc

from pug.component import *

from pig.util import get_gamedata
from pig.PigDirector import PigDirector
from pig.components import SpriteComponent

class Multiple_Lives(SpriteComponent):
    """This object has multiple lives and will respawn at its starting point
after being destroyed. IMPORTANT: This Component only works on objects with a 
class file.

This component gives the base object a new callback:
    on_respawn(): called after object respawns
"""
    #component_info
    _set = 'pig'
    _type = 'gameplay'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['start_lives', 'How many times the object can respawn\n'+\
                        'after being destroyed'],
            ['respawn_time', 
                    'Number of seconds between being destroyed and respawning'],
            ['do_gameover', 'When lives reach zero, call gamedata.gameover()'],
            ['value_name', 
                    'If this is not blank, number of lives remaining\n'+\
                    'will be stored in gamedata.<value_name>'],
            ['spawn_archetype', 'If this is an archetype, it\n'+\
                                'will spawn when scene starts.']
            ]
    #defaults
    spawn_archetype = True
    start_lives = 3
    respawn_time = 3
    value_name = 'lives'
    do_gameover = False
    
    _lives = None
    
    @component_method
    def on_scene_start(self):
        "Set lives at beginning of scene"
        self.get_lives()
    
    @component_method
    def on_destroy(self):
        if self.lives:
            self.lives -= 1
            (Delay(self.respawn_time) + CallFunc(do_respawn, 
                                                 self.owner.__class__,
                                                 self.lives,
                                                 PigDirector.scene)).do()
        elif self.do_gameover:
            gamedata = get_gamedata()
            gamedata.gameover()
            
    @component_method
    def on_delete(self):
        if self.owner.archetype and self.spawn_archetype and \
                getattr(PigDirector, 'start_project', False):
            # set up original lives
            (Delay(0) + CallFunc(self.owner.__class__)).do()
                                             
    @component_method
    def on_respawn(self):
        pass
            
    #making these component methods, gives you access at the base object level
    @component_method
    def set_lives(self, lives):
        "set_lives(lives): set self._lives"
        self._lives = lives
        if self.value_name:
            gamedata = get_gamedata()
            setattr(gamedata, self.value_name, lives)            
    @component_method
    def get_lives(self):
        "get_lives()->self._lives"
        if self._lives is None:
            self.set_lives( self.start_lives - 1)
        if self.value_name:
            gamedata = get_gamedata()         
            try:
                return getattr(gamedata, self.value_name)   
            except:
                return None
        else:
            return self._lives
    lives = property(get_lives, set_lives, doc = "Current lives") 
    
# this is in a separate function because the original object with the component
# has been deleted
def do_respawn( cls, lives, scene=None):
    #check to make sure we're in the same scene
    if scene and scene != PigDirector.scene:
        return
    obj = cls()
    obj.set_lives( lives)

register_component( Multiple_Lives)
