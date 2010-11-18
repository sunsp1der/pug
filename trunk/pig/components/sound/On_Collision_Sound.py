from Opioid2D.public.Node import Node

from pug.component import *

from pig.audio import get_sound
from pig.components import Collision_Callback
from pig.editor.agui import SoundFile 
import pig.audio

class On_Collision_Sound( Collision_Callback):
    """Owner plays a sound when destroyed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ["sound", SoundFile, {'doc':"The sound to play"}]
        ] + Collision_Callback._field_list 
    
    sound = None
    sound_object = None

    @component_method
    def on_added_to_scene(self):
        "Get the sound object"
        self.sound_object = get_sound( self.sound)

    @component_method
    def on_collision(self, toSprite, fromSprite, toGroup, fromGroup):
        "Play the sound when object collides"
        self.sound_object.play()
                
register_component( On_Collision_Sound)
    