import random

from Opioid2D import Vector
from Opioid2D.public.Node import Node

from pug.component import *

from pig.components import SpriteComponent

class Random_Motion(SpriteComponent):
    """Set a random velocity, rotation and spin on the object when it's added to 
a scene."""
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    _field_list = [
            ['angle','Base angle of movement'],
            ['angle_variance','Amount angle can vary in either direction'],
            ['velocity','Base velocity to set'],
            ['velocity_variance',
                        'Amount velocity can vary in either direction'],
            ['rotation','Base rotation speed to set'],
            ['rotation_variance',
                        'Amount rotation speed can vary in either direction'],           
            ['rotated',
                    'If owner is already rotated when motion is set, velocity '+ 
                    'and acceleration will be relative to that rotation.'],
            ['additive', 
             "Add to owner's current values instead of setting them."],
            ['align_rotation', 
             "Align owner's rotation to direction of movement"]
    ]
    #defaults
    angle = 0
    angle_variance = 180
    velocity = 20
    velocity_variance = 10
    rotation = 0
    rotation_variance = 0
    rotated = True
    additive = True
    align_rotation = True
        
    @component_method
    def on_added_to_scene(self):
        """Set the motion when object is added to scene"""
        self.set_motion()
        
    @component_method
    def set_motion(self):
        """Apply the motion settings"""
        owner = self.owner
        vector = Vector(0,0)
        vector.length = self.velocity + \
                random.uniform(-self.velocity_variance, self.velocity_variance)
        vector.direction = self.angle + \
                random.uniform(-self.angle_variance, self.angle_variance)
        rotation_speed = self.rotation + \
                random.uniform(self.rotation_variance, self.rotation_variance)
        if self.rotated:
            vector.direction += owner.rotation
        if self.additive:
            owner.velocity += vector
            owner.rotation_speed += rotation_speed
        else:
            owner.velocity = vector
            owner.rotation_speed = rotation_speed
        if self.align_rotation:
            owner.rotation = owner.velocity.direction
        
register_component( Random_Motion)
