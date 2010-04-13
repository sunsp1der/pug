from Opioid2D import AlphaFade, CallFunc, Delay
from Opioid2D.public.Node import Node

from pug.component import *

from pig.PigDirector import PigDirector

class Fade(Component):
    """Owner fades in and/or fades out."""
    #component_info
    _set = 'pig'
    _type = 'effect'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['fade_in_secs',
                    "Number of seconds to take fading in. -1 = no fade."],
            ['fade_out_secs',
"Number of seconds to take fading out when owner is destroyed. -1 = no fade."],
            ['fade_out_collisions','Allow object to collide while fading out']
            ]
    #defaults
    fade_in_secs = 3.0
    fade_out_secs = 3.0
    fade_out_collisions = False

    @component_method
    def on_added_to_scene(self, scene):
        """Do fade in if fade_in_secs > 0"""
        self.fade_in()
            
    def fade_in(self, secs=None, dstalpha=None):
        """fade_in(secs=None, dstalpha=None)
        
secs: number of seconds to take fading. Default: self.fade_in_secs
dstalpha: destination alpha to fade in to. Default: self.owner.alpha       
"""
        if secs is None:
            secs = self.fade_in_secs
        if  dstalpha is None:
            dstalpha = self.owner.alpha
        if secs >= 0:
            self.owner.set_alpha(0)
            self.owner.do( AlphaFade(dstalpha, secs))
        
    @component_method
    def on_destroy(self):
        if not self.fade_out_collisions:
            PigDirector.scene.unregister_collision_callback(self.owner)
#            self.owner.do( Delay(0) + CallFunc(
#                            PigDirector.scene.unregister_collision_callback,
#                            self.owner)
#                          )
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
