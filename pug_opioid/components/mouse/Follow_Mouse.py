from Opioid2D.public.Node import Node
from Opioid2D import RealTickFunc, Mouse

from pug.component import *

from pug_opioid.util import angle_to

class Follow_Mouse(Component):
    """Object follows the mouse pointer"""
    # component_info
    _set = 'pug_opioid'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]    
    _field_list = [
            ['face_movement','Rotate object to direction of motion']
            ]
    # attribute defaults
    face_movement = False
    # other defaults
    action = None

    @component_method
    def on_added_to_scene(self):
        """Start following when object is added to scene"""
        self.start_following_mouse()
        
    @component_method
    def start_following_mouse(self):
        "Start following the mouse pointer"
        if not self.action:
            self.action = RealTickFunc( self.follow).do()
        
    @component_method
    def stop_following_mouse(self):
        "Stop following the mouse pointer"
        if self.action: 
            self.action.end()

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
        
register_component( Follow_Mouse)
