from pug.component import *

from pig import PigScene
from pig.editor.agui import KeyDropdown, SoundFile
from pig.audio import get_sound
from pig.keyboard import keys

class On_Key_Sound_Scene( Component):
    """Scene plays a sound when key is pressed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [PigScene]
    # attributes:   
    _field_list = [
        ["key", KeyDropdown, {'doc':"The key that triggers the sound"}],
        ["sound", SoundFile, {'doc':"The sound to play"}]
        ]
    
    key = keys["S"]
    sound = None
    kinfo = None
    #TODO: Repeat sound while key down
    
    @component_method
    def on_start(self):
        "Get the sound object and set it to play when key is pressed"
        self.sound_object = get_sound( self.sound)
        self.kinfo = self.owner.register_key_down(self.key, self.play)

    def play(self):
        self.sound_object.play()

    @component_method
    def exit(self):
        "Unregister key"
        self.owner.unregister_key(self.kinfo)
    
register_component( On_Key_Sound_Scene)
    