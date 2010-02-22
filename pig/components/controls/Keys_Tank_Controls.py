from Opioid2D.public.Node import Node

from pug.component import *

from pig.keyboard import *
from pig.editor.agui import KeyDropdown

class Keys_Tank_Controls( Component):
    """Keys for forward, backward, and rotate left/right"""
    #component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['velocity', 'How fast object moves forward/backward'],
            ['rotation_speed', 'How fast object turns'],
            ['forward_key', KeyDropdown, 
                    {'doc':'Press this key to set objects forward velocity'}],
            ['backward_key', KeyDropdown, 
                    {'doc':'Press this key to set objects backward velocity'}],
            ['left_key', KeyDropdown, 
             {'doc':'Press this key to set objects leftward rotation speed'}],
            ['right_key', KeyDropdown, 
             {'doc':'Press this key to set objects rightward rotation speed'}],
            ]
    #defaults
    velocity = 50
    rotation_speed = 135
    forward_key = keys["UP"]
    backward_key = keys["DOWN"]
    left_key = keys["LEFT"]
    right_key = keys["RIGHT"]
                
    @component_method
    def on_added_to_scene(self, scene):
        """Set keys when object is added to scene"""
        scene.register_key_down( self.backward_key, self.move_key, 
                                 0, -self.velocity)
        scene.register_key_down( self.forward_key, self.move_key, 
                                 0, self.velocity)
        scene.register_key_down( self.left_key, self.move_key, 
                                 -self.rotation_speed, 0)
        scene.register_key_down( self.right_key, self.move_key, 
                                 self.rotation_speed, 0)
        scene.register_key_up( self.backward_key, self.move_key, 
                                 0, self.velocity)
        scene.register_key_up( self.forward_key, self.move_key, 
                                 0, -self.velocity)
        scene.register_key_up( self.left_key, self.move_key, 
                                 self.rotation_speed, 0)
        scene.register_key_up( self.right_key, self.move_key, 
                                 -self.rotation_speed, 0)
        
    def move_key(self, x_delta, y_delta):
        self.owner.velocity += (x_delta, 0)
                
register_component( Keys_Tank_Controls)

