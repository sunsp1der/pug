import weakref

from Opioid2D import RealTickFunc, CallFunc, Vector
from Opioid2D.public.Node import Node

from pug.component import *

from pig.components import SpriteComponent
from pig.util import angle_to

class Face_Motion(SpriteComponent):
    """Force owner to always face the direction that it's moving.
    
Warning: This component uses a tick_action, so it may be slow.
"""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['offset','Forward direction is offset by this much'],                   
            ]
    #defaults
    offset = 0
    #other defaults
    last_position = None
    tick_action = None
    
    @component_method
    def on_added_to_scene(self):
        """Start facing motion when object is added to scene"""
        self.set_face_motion()
                
    @component_method
    def set_face_motion(self):
        """set_face_motion(): Set object to face its motion."""
        self.tick_action = RealTickFunc( self.face_motion).do()
        self.face_motion()
        
    @component_method
    def on_delete(self):
        "Abort the tick action on delete"
        if self.tick_action:
            self.tick_action.abort()

    def face_motion(self):
        if not self.enabled:
            self.last_position=None
            return
        if self.last_position and tuple(self.owner.position)\
                                                        != self.last_position:
            self.owner.rotation = angle_to( self.last_position,
                                            self.owner.position)
        self.last_position = tuple(self.owner.position)

register_component( Face_Motion)
