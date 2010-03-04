from Opioid2D.public.Node import Node
from Opioid2D import RealTickFunc, Mouse

from pug.component import *

from pig.util import angle_to

class Mouse_Follow(Component):
    """Object follows the mouse pointer"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes:   
    _field_list = [
            ['face_movement','Rotate object to direction of motion']
            ]
    # attribute defaults
    face_movement = False
    # other defaults
    tick_action = None

    @component_method
    def on_added_to_scene(self, scene):
        """Start following when object is added to scene"""
        self.start_following_mouse()
        
    @component_method
    def start_following_mouse(self):
        "Start following the mouse pointer"
        if not self.tick_action:
            self.tick_action = RealTickFunc( self.follow).do()
        
    @component_method
    def stop_following_mouse(self):
        "Stop following the mouse pointer"
        if self.tick_action: 
            self.tick_action.abort()

    def follow(self):
        if not self.enabled:
            return
        owner = self.owner
        if not owner.layer:
            return
        mousepos = owner.layer.convert_pos(Mouse.position[0], Mouse.position[1])
        # convert from Opioid2D.Vector to simple co-ordinates 
        my_pos = (owner.position[0], owner.position[1]) 
        mousepos = (mousepos[0], mousepos[1])
        if my_pos != mousepos:
            if self.face_movement:
                owner.rotation = angle_to(my_pos, mousepos)
            owner.position = mousepos
        
register_component( Mouse_Follow)
