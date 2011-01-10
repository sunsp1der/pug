from pug.component import *

from pig import Scene
from pig.components.sound.Key_Sound import Key_Sound

class Key_Sound_Scene( Key_Sound):
    """Scene plays a sound when key is pressed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Scene]
    # attributes:   
    
    @component_method
    def on_start(self):
        "Get the sound object and set it to play when key is pressed"
        self.setup()

    @component_method
    def exit(self):
        "Unregister key"
        self.unregister_keys()
    
register_component( Key_Sound_Scene)
    