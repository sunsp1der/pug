from pug.component import *

from pig import PigScene
from pig.components.sound.On_Key_Sound import On_Key_Sound

class On_Key_Sound_Scene( On_Key_Sound):
    """Scene plays a sound when key is pressed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [PigScene]
    # attributes:   
    
    @component_method
    def on_start(self):
        "Get the sound object and set it to play when key is pressed"
        self.setup()

    @component_method
    def exit(self):
        "Unregister key"
        self.unregister_keys()
    
register_component( On_Key_Sound_Scene)
    