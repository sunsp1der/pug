import random
from Opioid2D import Vector
from Opioid2D.public.Node import Node
from pug.component import *

class Random_Motion(Component):
    """Set a random velocity, rotation and spin on the object when it's added to 
a scene."""
    _set = 'pig'
    _type = 'physics'
    _class_list = [Node]
    _field_list = [
            ['angle_min', 'Minimum angle of movement'],
            ['angle_max', 'Maximum angle of movement'],
            ['velocity_min', 'Minimum velocity to set'],
            ['velocity_max', 'Maximum velocity to set'],
            ['rotation_speed_min', 'Minimum rotation speed to set'],
            ['rotation_speed_max', 'Maximum rotation speed to set'],
            ['rotated',
"""If owner is already rotated when motion is set, velocity 
and acceleration will be relative to that rotation."""],
            ['additive', 
             "Add to owner's current values instead of setting them."],
            ['align_rotation', 
             "Align owner's rotation to direction of movement"]
    ]
    #defaults
    angle_min = 0
    angle_max = 360
    velocity_min = 10
    velocity_max = 25
    rotation_speed_min = 0
    rotation_speed_max = 0
    rotated = True
    additive = True
    align_rotation = True
        
    @component_method
    def on_added_to_scene(self, scene):
        """Set the motion when object is added to scene"""
        self.set_motion()
        
    @component_method
    def set_motion(self):
        """Apply the motion settings"""
        owner = self.owner
        vector = Vector(0,0)
        vector.length = random.uniform(self.velocity_min, self.velocity_max)
        vector.direction = random.uniform(self.angle_min, self.angle_max)
        rotation_speed = random.uniform(self.rotation_speed_min, 
                                        self.rotation_speed_max)
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
