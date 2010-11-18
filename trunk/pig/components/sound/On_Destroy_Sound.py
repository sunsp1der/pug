from Opioid2D.public.Node import Node

from pug.component import *

from pig.audio import get_sound
from pig.editor.agui import SoundFile

class On_Destroy_Sound( Component):
    """Owner plays a sound when destroyed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ["sound", SoundFile, {'doc':"The sound to play"}]
        ]
    
    sound = None
    sound_object = None
    
    @component_method
    def on_added_to_scene(self):
        "Get the sound object"
        self.sound_object = get_sound( self.sound)

    @component_method
    def on_destroy(self):
        "Play the sound when object is destroyed"
        self.sound_object.play()
    
register_component( On_Destroy_Sound)
    