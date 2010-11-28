from Opioid2D.public.Node import Node

from pug.component import *
from pug import FloatSpin

from pig.audio import get_sound
from pig.editor.agui import SoundFile
from pig.components import On_Create_Sound

class On_Destroy_Sound( On_Create_Sound):
    """Owner plays a sound when destroyed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = []    
    _field_list += On_Create_Sound._field_list
    # defaults
    sound = None
    volume = 1.0
    
    sound_object = None    
        
    @component_method
    def on_added_to_scene(self):
        "Set up the sound object"
        self.setup()

    @component_method
    def on_destroy(self):
        "Play the sound when object is destroyed"
        self.sound_object.play()
    
register_component( On_Destroy_Sound)
    