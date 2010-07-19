from Opioid2D.public.Node import Node

from pug.component import *

from pig.util import GameData

class Score_On_Destroy(Component):
    "When object is destroyed, add a value to GameData.score"
    #component_info
    _set = 'pig'
    _type = 'gameplay'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['value','Add this to GameData.score when destroyed'],                   
            ]
    #defaults
    value = 1
    
    @component_method
    def on_destroy(self):
        """Add score when object is destroyed"""
        try:
            GameData.score += self.value
        except:
            GameData.score = self.value

register_component( Score_On_Destroy)
