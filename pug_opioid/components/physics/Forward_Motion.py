from Opioid2D import RealTickFunc, CallFunc, Vector
from Opioid2D.public.Node import Node

from pug.component import *

class Forward_Motion(Component):
    """Apply velocity or acceleration in the direction the object is facing.
    
Warning: This component uses a tick_action, so it may be slow."""
    #component_info
    _set = 'pug_opioid'
    _type = 'physics'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['velocity','Forward velocity'],
            ['acceleration',
'Forward acceleration. Velocity must be set to 0 for this to work.'],
            ['offset','Forward direction is offset by this much'],
            ]
    #defaults
    velocity = 0
    acceleration = 100
    offset = 0
    #other defaults
    tick_action = None
    last_rotation = None
    
    @component_method
    def on_added_to_scene(self, scene):
        """Start facing target when object is added to scene"""
        self.set_forward_motion()
        
    @component_method
    def set_forward_motion(self, velocity=None, acceleration=None):
        """set_forward_motion(self, velocity=None, acceleration=None)
        
Set object's forward velocity and acceleration. Arguments default to component
values (self.velocity and self.acceleration)"""
        if velocity == None:
            velocity = self.velocity
        else:
            self.velocity = velocity
        self.velocity_vector = Vector(0, -velocity)
        self.velocity_vector.direction = self.offset
        if acceleration == None:
            acceleration = self.acceleration
        else:
            self.acceleration = acceleration
        self.acceleration_vector = Vector(0, -acceleration)
        self.acceleration_vector.direction = self.offset
        if self.tick_action:
            self.tick_action.abort()
        if velocity or acceleration:
            self.tick_action = RealTickFunc( self.forward_motion).do()
            self.forward_motion()
        
    @component_method
    def on_delete(self):
        "Abort the tick action on delete"
        if self.tick_action:
            self.tick_action.abort()            
        
    def forward_motion(self):
        if not self.enabled:
            return
        if self.owner.rotation == self.last_rotation:
            return
        if self.velocity:
            self.velocity_vector.direction = self.owner.rotation + self.offset
            self.owner.velocity = self.velocity_vector
        if self.acceleration:
            self.acceleration_vector.direction = self.owner.rotation+self.offset
            self.owner.acceleration = self.acceleration_vector
        self.last_rotation = self.owner.rotation
        
        
register_component( Forward_Motion)
