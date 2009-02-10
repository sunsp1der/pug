from Opioid2D import AlphaFade, CallFunc
from Opioid2D.public.Node import Node

from pug.component import *

class Fade(Component):
    """Owner fades in and/or fades out."""
    #component_info
    _set = 'pug_opioid'
    _type = 'effect'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['fade_in_secs',
                    "Number of seconds to take fading in. 0 = no fade."],
            ['fade_in_alpha', "Fade in to this alpha value"],
            ['fade_out_secs',
   "Number of seconds to take fading out when owner is destroyed. 0 = no fade."]
            ]
    #defaults
    fade_in_secs = 3.0
    fade_in_alpha = 1.0
    fade_out_secs = 3.0

    @component_method
    def on_added_to_scene(self):
        """Do fade in if fade_in_secs > 0"""
        self.fade_in()
            
    def fade_in(self, secs=None, dstalpha=None):
        """fade_in(secs=None, dstalpha=None)
        
secs: number of seconds to take fading. Default: self.fade_in_secs
dstalpha: destination alpha to fade in to. Default: self.fade_in_alpha        
"""
        if secs is None:
            secs = self.fade_in_secs
        if  dstalpha is None:
            dstalpha = self.fade_in_alpha
        if secs >= 0:
            self.owner.set_alpha(0)
            self.owner.do( AlphaFade(dstalpha, secs))
        
    @component_method
    def on_destroy(self):
        self.fade_out()
        
    def fade_out(self, secs=None):
        "fade_out(secs=None): fade owner out. secs default: self.fade_out_secs"
        if secs is None:
            secs = self.fade_out_secs
        if secs >= 0:
            self.owner.block_destroy(self)
            self.owner.do( AlphaFade(0.0, secs) + \
                    CallFunc(self.owner.block_destroy, self, block=False))

register_component(Fade)
