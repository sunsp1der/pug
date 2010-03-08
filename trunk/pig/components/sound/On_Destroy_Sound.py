import pygame

from Opioid2D.public.Node import Node

from pug.component import *
from pug import Filename

from pig.audio import get_sound

class On_Destroy_Sound( Component):
    """Owner plays a sound when destroyed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ["sound", Filename, {'doc':"The sound to play",'subfolder':'sounds'}]
        ]
    
    sound = None
    
    @component_method
    def on_added_to_scene(self, scene):
        "Get the sound object"
        self.soundObject = get_sound( self.sound)

    @component_method
    def on_destroy(self):
        "Play the sound when object is destroyed"
        self.soundObject.play()
    
register_component( On_Destroy_Sound)
    