from Opioid2D import Director

from pug.component import *

from pig import PigScene
from pig.audio import get_sound
from pig.editor.agui import SoundFile 

class On_Start_Sound( Component):
    """Play a sound when the scene starts"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [PigScene]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
        ["sound", SoundFile, {'doc':"The sound to play"}]
        ]
    #defaults
    sound = None
    
    @component_method
    def on_start(self):
        "Get and play the sound object"
        self.soundObject = get_sound( self.sound)
        self.soundObject.play()        
        
register_component( On_Start_Sound)