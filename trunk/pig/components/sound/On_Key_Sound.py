import pygame

from Opioid2D.public.Node import Node

from pug.component import *
from pug import Filename

from pig.editor.agui import KeyDropdown
from pig.audio import get_sound
from pig.keyboard import keys
from pig import PigDirector

class On_Key_Sound( Component):
    """Owner plays a sound when key is pressed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ["key", KeyDropdown, {'doc':"The key that triggers the sound"}],
        ["sound", Filename, {'doc':"The sound to play",'subfolder':'sounds'}]
        ]
    
    key = keys["S"]
    sound = None
    #TODO: Repeat sound while key down
    
    @component_method
    def on_added_to_scene(self, scene):
        "Get the sound object"
        self.soundObject = get_sound( self.sound)
        self.kinfo = scene.register_key_down(self.key, self.play)

    def play(self):
        self.soundObject.play()

    @component_method
    def on_destroy(self):
        "Play the sound when object is destroyed"
        PigDirector.scene.unregister_key(self.kinfo)
    
register_component( On_Key_Sound)
    