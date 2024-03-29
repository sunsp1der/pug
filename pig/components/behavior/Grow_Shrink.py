from Opioid2D import ScaleTo, CallFunc
from Opioid2D.public.Node import Node

from pug.component import *

from pig.PigDirector import PigDirector
from pig.components import SpriteComponent

class Grow_Shrink(SpriteComponent):
    """Object grows into scene and/or shrinks away when destroyed."""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['grow_in_secs',
                    "Number of seconds to take growing in. -1 = no grow in."],
            ['shrink_out_secs',
                    "Number of shrink-out seconds when owner is"+\
                    "destroyed. -1 = no shrink outs."],
            ['shrink_out_collisions',
                    'Allow object to collide while shrinking out']            
            ]
    #defaults
    grow_in_secs = 3.0
    shrink_out_secs = 3.0
    shrink_out_collisions = False

    @component_method
    def on_first_display(self):
        """Start the grow-in"""
        self.grow_in()
            
    def grow_in(self, secs=None, dstscale=None):
        """grow_in(secs=None, dstscale=None)
        
secs: number of seconds to take growing. Default: self.grow_in_secs
dstscale: destination scale to grow to. Default: self.owner.scale        
"""
        if secs is None:
            secs = self.grow_in_secs
        if  dstscale is None:
            dstscale = tuple(self.owner.scale)
        if secs >= 0:
            self.owner.set_scale((0,0))
            self.owner.do( ScaleTo(dstscale, secs))
        
    @component_method
    def on_destroy(self):
        "Shrink out the object"
        if not self.shrink_out_collisions:
            PigDirector.scene.unregister_collision_callback(self.owner)        
        self.shrink_out()
        
    def shrink_out(self, secs=None):
        """shrink_out(secs=None): shrink owner out

secs: number of secs to shrink out. default: self.shrink_out_secs"""
        if secs is None:
            secs = self.shrink_out_secs
        if secs >= 0:
            self.owner.block_destroy(self)
            self.owner.do( ScaleTo(0.0, secs) + \
                    CallFunc(self.owner.block_destroy, self, block=False))

register_component(Grow_Shrink)
