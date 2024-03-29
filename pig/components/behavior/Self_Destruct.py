from Opioid2D import CallFunc, Delay
from Opioid2D.public.Node import Node

from pug.component import *

from pig.components import SpriteComponent

class Self_Destruct(SpriteComponent):
    """Object self-destructs after a given amount of time."""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['timer_secs', "Seconds before object self destructs"],
            ['start_automatically', """Start timer when owner is added to scene.
Otherwise, use this component's 'start_timer' method."""],
            ]
    #defaults
    timer_secs = 3.0
    start_automatically = True
    
    timerAction = None # this can be aborted if necessary
    
    @component_method
    def on_added_to_scene(self):
        """Start timer when object is added to scene"""
        if self.start_automatically:
            self.start_timer()
        
    def start_timer(self, secs=None):
        "start_timer(secs=None): If secs is none, default to self.timer_secs"
        if secs is None:
            secs = self.timer_secs
        self.timerAction = self.owner.do( Delay(secs) + CallFunc(self.destruct))
        
    def destruct(self):
        self.timerAction = None
        self.owner.destroy()
        
    def abort_timer(self):
        "abort_timer(): Abort the self destruction"
        if self.timerAction:
            self.timerAction.abort()

register_component( Self_Destruct)
