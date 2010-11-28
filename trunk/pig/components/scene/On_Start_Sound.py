from pug.component import *

from pig import PigScene
from pig.components.scene.Key_Sound_Scene import Key_Sound_Scene
from pig.components import On_Create_Sound

class On_Start_Sound( Key_Sound_Scene):
    """Play a sound when the scene starts. Useful for background music."""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [PigScene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = []
    _field_list += On_Create_Sound._field_list
    _field_list += Key_Sound_Scene._loop_fields
    #defaults
    sound = None
    key = None
    loops = -1
    
    @component_method
    def on_start(self):
        "Get and play the sound object"
        self.setup()
        self.play()        
        
    @component_method
    def on_exit(self):
        "Stop the sound"
        self.stop()
        
register_component( On_Start_Sound)