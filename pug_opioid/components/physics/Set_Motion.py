from Opioid2D.public.Node import Node
from pug.component import *

class Set_Motion(Component):
    """Set object's velocity, acceleration, rotation and friction when it's
added to a scene."""
    _set = 'pug_opioid'
    _type = 'physics'
    _class_list = [Node]
    _attribute_list = [
            ['velocity_x', 'Horizontal velocity'],
            ['velocity_y', 'Vertical velocity'],
            ['acceleration_x', 'Horizontal acceleration'],
            ['acceleration_y', 'Vertical acceleration'],
            ['rotation_speed', 'Clockwise rotational velocity'],
            ['friction', '0-1 multiplier applied every realtick'],
            ['additive', 
       "Add to current values instead of setting them. Friction is multiplied."]
    ]
    #defaults
    velocity_x=0
    velocity_y=0
    acceleration_x=0
    acceleration_y=0
    rotation_speed=0
    friction=1.0
    additive = False
    
    @component_method
    def on_added_to_scene(self):
        """Set the rotation when object is added to scene"""
        owner = self.owner
        if self.additive:
            owner.velocity = (owner.velocity[0] + self.velocity_x,
                              owner.velocity[1] + self.velocity_y)
            owner.acceleration = (owner.acceleration[0] + self.acceleration_x,
                              owner.acceleration[1] + self.acceleration_y)
            owner.rotation_speed += self.rotation_speed
            owner.friction = owner.friction * self.friction
        else:
            owner.velocity = (self.velocity_x, self.velocity_y)
            owner.acceleration = (self.acceleration_x, self.acceleration_y)
            owner.rotation_speed = self.rotation_speed
            owner.friction = self.friction
        
register_component( Set_Motion)
