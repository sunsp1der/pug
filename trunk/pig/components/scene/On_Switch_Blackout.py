import Opioid2D

from pug.component import *

from pig import Scene, Sprite
from pig.actions import *
from pig.PigDirector import PigDirector

class On_Switch_Blackout( Component):
    """Create a blackout effect when switching away from scene."""
    # component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Scene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['blackout_secs','Seconds to take blacking out'],
            ]
    #defaults
    blackout_secs = 1
    
    @component_method
    def on_switch_scene(self, scene):
        "Create a blackout sprite and start it fading in"
        PigDirector.scene.add_layer("overlay")
        sprite = Sprite()
        sprite.set_layer("overlay")
        sprite.image_file = "art/block.png"
        size = Opioid2D.Display.get_view_size()
        sprite.scale = (size[0]/2,size[1]/2)
        sprite.tint = (0,0,0)
        sprite.alpha = 0
        sprite.position = sprite.scale
        PigDirector.scene.block_switch_scene( sprite)
        sprite.do( AlphaFade(1,self.blackout_secs) + \
                   CallFunc(PigDirector.scene.block_switch_scene, sprite, False)
                   )
        
register_component( On_Switch_Blackout)