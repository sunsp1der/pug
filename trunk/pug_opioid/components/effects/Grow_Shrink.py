from Opioid2D import ScaleTo, CallFunc
from Opioid2D.public.Node import Node

from pug.component import *

class Grow_Shrink(Component):
    """Owner grows into scene and/or shrinks away when destroyed."""
    #component_info
    _set = 'pug_opioid'
    _type = 'effect'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['grow_in_secs',
                    "Number of seconds to take growing in. 0 = no grow."],
            ['grow_in_alpha', "Fade in to this alpha value"],
            ['grow_out_secs',
   "Number of seconds to take fading out when owner is destroyed. 0 = no grow."]
            ]
    #defaults
    grow_in_secs = 3.0
    grow_in_scale = (1.0, 1.0)
    shrink_out_secs = 3.0

    @component_method
    def on_added_to_scene(self):
        """Do grow in if grow_in_secs > 0"""
        self.grow_in()
            
    def grow_in(self, secs=None, dstscale=None):
        """grow_in(secs=None, dstscale=None)
        
secs: number of seconds to take growing. Default: self.grow_in_secs
dstscale: destination scale to grow to. Default: self.grow_in_alpha        
"""
        if secs is None:
            secs = self.grow_in_secs
        if  dstscale is None:
            dstscale = self.grow_in_scale
        if secs >= 0:
            self.owner.set_scale((0,0))
            self.owner.do( ScaleTo(dstscale, secs))
        
    @component_method
    def on_destroy(self):
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
