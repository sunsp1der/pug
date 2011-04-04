from Opioid2D.public.Node import Node

from pug.component import *

from pig.util import get_gamedata
from pig.components import SpriteComponent
from pig.components import Value_On_Destroy

class Value_On_Create(Value_On_Destroy):
    "When object is created, change a gamedata value"
    #component_info
    _set = 'pig'
    _type = 'gameplay'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
#    _field_list = [
#            ['amount','Add this to gamedata.value_name'],                   
#            ['value_name','The name of the gamedata attribute to affect' ],
#            ]
    #defaults
    value_name = 'score'
    amount = 1
    
    on_destroy = None # remove Value_On_Destroy's method
    
    @component_method
    def on_added_to_scene(self):
        """Add self.amount to gamedata.<value_name> when object is created"""
        gamedata = get_gamedata()        
        setattr(gamedata, self.value_name, 
                getattr(gamedata, self.value_name, 0) + self.amount)

register_component( Value_On_Create)
