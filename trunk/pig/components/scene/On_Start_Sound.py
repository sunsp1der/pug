from pug.component import *

from pig import PigScene
from pig.components.scene.On_Key_Sound_Scene import On_Key_Sound_Scene

class On_Start_Sound( On_Key_Sound_Scene):
    """Play a sound when the scene starts. Useful for background music."""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [PigScene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = On_Key_Sound_Scene._field_list[1:]
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