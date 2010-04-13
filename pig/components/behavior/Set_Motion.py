from Opioid2D import Vector
from Opioid2D.public.Node import Node
from pug.component import *

class Set_Motion(Component):
    """Set owner's velocity, acceleration, rotation and friction when it's
added to a scene."""
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    _field_list = [
            ['velocity_x', 'Horizontal velocity'],
            ['velocity_y', 'Vertical velocity'],
            ['acceleration_x', 'Horizontal acceleration'],
            ['acceleration_y', 'Vertical acceleration'],
            ['rotation_speed', 'Clockwise rotational velocity'],
            ['friction', '0-1 multiplier applied every realtick'],
            ['rotated',
"""If owner is already rotated when motion is set, velocity 
and acceleration will be relative to that rotation."""],
            ['additive', 
"""Add to owner's current values instead of setting them. 
Friction is multiplied."""],
    ]
    #defaults
    velocity_x = 0
    velocity_y = 0
    acceleration_x = 0
    acceleration_y = 0
    rotation_speed = 0
    friction = 1.0
    rotated = True
    additive = True
        
    @component_method
    def on_added_to_scene(self, scene):
        """Set the motion when object is added to scene"""
        self.set_motion()
        
    def set_motion(self):
        """Apply the motion settings"""
        owner = self.owner
        velocity_vector = Vector(self.velocity_x, self.velocity_y)
        acceleration_vector = Vector(self.acceleration_x, self.acceleration_y)
        if self.rotated:
            velocity_vector.direction += owner.rotation
            acceleration_vector.direction += owner.rotation
        if self.additive:
            owner.velocity += velocity_vector
            owner.acceleration += acceleration_vector
            owner.rotation_speed += self.rotation_speed
            owner.friction = owner.friction * self.friction
        else:
            owner.velocity = velocity_vector
            owner.acceleration = acceleration_vector
            owner.rotation_speed = self.rotation_speed
            owner.friction = self.friction
        
register_component( Set_Motion)
