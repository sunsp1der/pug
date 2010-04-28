from Opioid2D import RealTickFunc, Vector
from Opioid2D.public.Node import Node

from pug.component import *

class Forward_Motion(Component):
    """Apply velocity or acceleration in the direction the object is facing.
    
Warning: This component uses a tick_action, so it may be slow."""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['speed','Forward velocity or acceleration'],
            ['accelerate',"If True, 'speed' indicates acceleration.\n"+\
                            "If False, 'speed' indicates velocity"],
            ]
    #defaults
    speed = 200
    accelerate = True

    offset = 0 # decided to hide this from the component gui, but it still works
    actual_offset = 0
    tick_action = None
    last_rotation = None
    
    @component_method
    def on_added_to_scene(self, scene):
        """Start facing target when object is added to scene"""
        self.set_forward_motion()
        
    @component_method
    def set_forward_motion(self, speed=None):
        """set_forward_motion(self, speed=None)
        
speed: set object's forward velocity or acceleration to this value. Defaults to
        self.speed
"""
        if speed == None:
            speed = self.speed
        else:
            self.speed = speed
        if self.speed < 0:
            self.actual_offset = self.offset + 180
        else:
            self.actual_offset = self.offset
        self.speed_vector = Vector(0, -speed)

        if speed:
            if not self.tick_action:
                self.tick_action = RealTickFunc(self.update_forward_motion)
                self.tick_action.do()
        else:
            if self.tick_action:
                self.tick_action.abort()            
                self.tick_action = None
            self.last_rotation = None
            self.set_motion()            
        
    @component_method
    def on_destroy(self):
        "Abort the tick action on destroy"
        if self.tick_action:
            self.tick_action.abort()                  

    def set_motion(self):
        self.speed_vector.direction = self.owner.rotation + self.actual_offset
        if self.accelerate:
            self.owner.acceleration = self.speed_vector
        else:
            self.owner.velocity = self.speed_vector
            
    def update_forward_motion(self):
        if not self.enabled:
            return
        if self.owner.rotation == self.last_rotation:
            return        
        self.set_motion()        
        self.last_rotation = self.owner.rotation
        
        
register_component( Forward_Motion)
