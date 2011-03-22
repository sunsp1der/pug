import Opioid2D

from pug.component import *

from pig import Scene, Sprite
from pig.actions import *
from pig.PigDirector import PigDirector

class On_Start_Blackout( Component):
    """Start with a blackout effect when entering scene."""
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
    def on_start(self):
        "Create a blackout sprite and start it fading out"
        PigDirector.scene.add_layer("overlay")
        sprite = Sprite()
        sprite.set_layer("overlay")
        sprite.image_file = "art/block.png"
        size = Opioid2D.Display.get_view_size()
        sprite.scale = (size[0]/2,size[1]/2)
        sprite.tint = (0,0,0)
        sprite.position = sprite.scale
        sprite.do( AlphaFade(0,self.blackout_secs) + \
                   CallFunc(PigDirector.scene.delete_layer, "overlay")
                   )
        
register_component( On_Start_Blackout)