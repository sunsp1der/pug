import threading

from Opioid2D import RealTickFunc, CallFunc, Vector
from Opioid2D.public.Node import Node

from pug.component import *

class Face_Motion(Component):
    """Force owner to always face the direction that it's moving.
        
Warning: This component uses a tick_action, so it may be slow.
"""
    #component_info
    _set = 'pug_opioid'
    _type = 'physics'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['offset','Forward direction is offset by this much'],                   
            ]
    #defaults
    offset = 0
    #other defaults
    tick_action = None
    last_velocity = None
    
    @component_method
    def on_added_to_scene(self):
        """Start facing motion when object is added to scene"""
        self.set_face_motion()
        
    @component_method
    def set_face_motion(self):
        """set_face_motion(self)
        
Set object to face its motion."""
        self.tick_action = RealTickFunc( self.face_motion)
        self.tick_action.do()
        self.face_motion()
        
    def face_motion(self):
        if not self.enabled:
            return
        self.owner.rotation = self.owner.velocity.direction
        
        
register_component( Face_Motion)
