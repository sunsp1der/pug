from Opioid2D.public.Node import Node

from pug.component import *

from pig.audio import get_sound
from pig.components.sound.On_Create_Sound import On_Create_Sound

class On_Damaged_Sound( On_Create_Sound):
    """Owner plays a sound when it takes damage"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = []    
    _field_list += On_Create_Sound._field_list
    
    @component_method
    def on_added_to_scene(self):
        "Set up the sound object"
        self.setup()
    
    @component_method
    def on_take_damage(self, amount, damage, health):
        "Play the sound when object takes damage"
        self.sound_object.play()
    
register_component( On_Damaged_Sound)
    