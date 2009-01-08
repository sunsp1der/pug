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
    _attribute_list = [
            ['face_movement','Rotate object to direction of motion']
            ]
    #defaults
    face_movement = False

    @component_method
    def on_added_to_scene(self):
        """Set the rotation when object is added to scene"""
        act = RealTickFunc( self.follow)
        act.do()
        
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
