from Opioid2D.public.Node import Node

from pug.component import *
from pug import FloatSpin

from pig.audio import get_sound
from pig.components import SpriteComponent
from pig.editor.agui import SoundFile
from pig.PigDirector import PigDirector

class On_Create_Sound( SpriteComponent):
    """Owner plays a sound when it's added to a scene"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ["sound", SoundFile, {'doc':"The sound to play", 'volume':'volume'}],
        ["volume", FloatSpin, {'doc':"Sound volume", 'range':(0,1),
                               'digits':1, 'adjust_digits':True}],    
        ]
    sound = None
    volume = 1.0
    
    sound_object = None    
    
    @component_method
    def on_added_to_scene(self):
        "Get the sound object"
        self.setup()
        self.sound_object.play()
        
    def setup(self):
        "setup(): Set up the sound. This is for ease of derivation."
        scene = PigDirector.scene #@UndefinedVariable
        self.sound_object = get_sound( self.sound, volume=self.volume)                
            
register_component( On_Create_Sound)
    