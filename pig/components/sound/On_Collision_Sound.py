from Opioid2D.public.Node import Node

from pug.component import *

from pig.components import Collision_Callback, On_Create_Sound

class On_Collision_Sound( Collision_Callback, On_Create_Sound):
    """Owner plays a sound when destroyed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = []    
    _field_list += On_Create_Sound._sound_fields
    _field_list += Collision_Callback._field_list 

    @component_method
    def on_added_to_scene(self):
        "Set up the sound object and collision callback"
        self.setup()
        Collision_Callback.on_added_to_scene(self)

    @component_method
    def on_collision(self, toSprite, fromSprite, toGroup, fromGroup):
        "Play the sound when object collides"
        self.sound_object.play()
                
register_component( On_Collision_Sound)
    