from pug.component import *

from pig import Scene
from pig.actions import *
from pig.editor.agui import ScenesDropdown

from pig.PigDirector import PigDirector

class Scene_Timer( Component):
    """Automatically change to a different scene after a given amount of 
time."""
    # component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Scene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['scene_time','Seconds before scene changes'],
            ['next_scene',ScenesDropdown,{'doc':'Scene to change to',
                                          'component':True}]
            ]
    #defaults
    scene_time = 5
    next_scene = None
    
    @component_method
    def on_start(self):
        "Get and play the sound object"
        (Delay(self.scene_time) + CallFunc(PigDirector.switch_scene_to,
                                                  self.next_scene)).do()       

register_component( Scene_Timer)