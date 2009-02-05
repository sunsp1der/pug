from Opioid2D import RealTickFunc, CallFunc, Vector
from Opioid2D.public.Node import Node

from pug.component import *

class Forward_Motion(Component):
    """Apply velocity or acceleration in the direction the object is facing.
    
Warning: This component may cause major slow-downs."""
    #component_info
    _set = 'pug_opioid'
    _type = 'physics'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['velocity','Forward velocity'],
            ['acceleration','Forward acceleration'],
            ['offset','Forward direction is offset by this much'],
            ]
    #defaults
    velocity = 0
    acceleration = 100
    offset = 0
    #other defaults
    tick_action = None
    last_rotation = None
    old_velocity_vector = None
    
    @component_method
    def on_added_to_scene(self):
        """Start facing target when object is added to scene"""
        self.set_forward_motion()
        
    @component_method
    def set_forward_motion(self, velocity=None, acceleration=None):
        """set_forward_motion(self, velocity=None, acceleration=None)
        
Set object's forward velocity and acceleration. Arguments default to component
values (self.velocity and self.acceleration)"""
        if not self.old_velocity_vector:
            self.old_velocity_vector = Vector(0,0)
            self.old_acceleration_vector = Vector(0,0)
            self.new_velocity_vector = Vector(0,0)
            self.new_acceleration_vector = Vector(0,0)
        if velocity == None:
            velocity = self.velocity
        else:
            self.velocity = velocity
        if acceleration == None:
            acceleration = self.acceleration
        else:
            self.acceleration = acceleration
        if velocity or acceleration:
            self.tick_action = RealTickFunc( self.forward_motion)
            self.tick_action.do()
            self.forward_motion()
        else:
            if self.tick_action:
                self.tick_action.abort()
        
    def forward_motion(self):
        if not self.enabled:
            return
        if self.owner.rotation == self.last_rotation:
            return
        if self.velocity:
            if self.last_rotation is not None:
                self.old_velocity_vector.set_radial((self.last_rotation + \
                                                    self.offset, self.velocity))
            self.new_velocity_vector.set_radial((self.owner.rotation + \
                                              self.offset, self.velocity))
            self.owner.velocity += \
                            self.new_velocity_vector - self.old_velocity_vector
        if self.acceleration:
            if self.last_rotation is not None:
                self.old_acceleration_vector.set_radial((self.last_rotation + \
                                                self.offset, self.acceleration))
            self.new_acceleration_vector.set_radial((self.owner.rotation+self.offset,
                                         self.acceleration))
            self.owner.acceleration += \
                    self.new_acceleration_vector - self.old_acceleration_vector
        self.last_rotation = self.owner.rotation
        
        
register_component( Forward_Motion)
