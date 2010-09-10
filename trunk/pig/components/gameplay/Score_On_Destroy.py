from Opioid2D.public.Node import Node

from pug.component import *

from pig.util import get_gamedata

class Score_On_Destroy(Component):
    "When object is destroyed, change a gamedata value"
    #component_info
    _set = 'pig'
    _type = 'gameplay'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['amount','Add this to gamedata.value_name when destroyed'],                   
            ['value_name','The name of the gamedata attribute to affect' ],
            ]
    #defaults
    value_name = 'score'
    amount = 1
    
    @component_method
    def on_destroy(self):
        """Add score when object is destroyed"""
        gamedata = get_gamedata()        
        setattr(gamedata, self.value_name, 
                getattr(gamedata, self.value_name, 0) + self.amount)

register_component( Score_On_Destroy)
