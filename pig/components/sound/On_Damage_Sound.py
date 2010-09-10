from Opioid2D.public.Node import Node

from pug.component import *

from pig.audio import get_sound
from pig.editor.agui import SoundFile

class On_Damage_Sound( Component):
    """Owner plays a sound when it deals damage to something"""
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
    def on_added_to_scene(self, scene):
        "Get the sound object"
        self.sound_object = get_sound( self.sound)

    @component_method
    def on_deal_damage(self, target, amount):
        "Play the sound when object deals damage"
        self.sound_object.play()
    
register_component( On_Damage_Sound)
    