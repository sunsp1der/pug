from Opioid2D import Vector
from Opioid2D.public.Node import Node
from pug.component import *

class Stop_Motion_On_Destroy(Component):
    """Set owner's velocity, acceleration, and/or rotation to zero when object 
is destroyed. This is useful when object is still visible but fading out, 
shrinking out, or etc."""
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    _field_list = [
            ['zero_velocity', 'Set velocity to zero when object is destroyed'],
            ['zero_acceleration', 
                        'Set acceleration to zero when object is destroyed'],
            ['zero_rotation', 'Set rotation to zero when object is destroyed'],
    ]
    #defaults
    zero_velocity = True
    zero_acceleration = True
    zero_rotation = True
        
    @component_method
    def on_destroy(self):
        """Set stuff to zero when object is destroyed"""
        if self.zero_velocity:
            self.owner.velocity = (0,0)
        if self.zero_acceleration:
            self.owner.acceleration = (0,0)
        if self.zero_rotation:
            self.owner.rotation_speed = 0
        
register_component( Stop_Motion_On_Destroy)
