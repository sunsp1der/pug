from Opioid2D.public.Node import Node
from Opioid2D import Delay, CallFunc

from pug.component import *

from pig.util import get_gamedata

class Multiple_Lives(Component):
    """This object has multiple lives and will respawn at its starting point
after being destroyed.
This component gives the base object a new callback:
    on_respawn(): called after object respawns

IMPORTANT: This Component only works on objects with a class file.
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
            ['value_name', 
                    'If this is not blank, number of lives remaining\n'+\
                    'will be stored in gamedata.<value_name>']
            ]
    #defaults
    start_lives = 3
    respawn_time = 3
    value_name = 'lives'
    
    _lives = 0
      
    @component_method
    def on_first_display(self):
        "Set up multiple lives"
        self.lives = int(self.start_lives)
        
    @component_method
    def on_destroy(self):
        self.lives -= 1
        if self.lives:
            (Delay(self.respawn_time) + CallFunc(do_respawn, 
                                                 self.owner.__class__,
                                                 self.lives)).do()
                                             
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
        return self._lives
    lives = property(get_lives, set_lives, doc = "Current lives") 
    
# this is in a separate function because the original object with the component
# has been deleted
def do_respawn( cls, lives):
    obj = cls()
    obj.set_lives( lives)

register_component( Multiple_Lives)
