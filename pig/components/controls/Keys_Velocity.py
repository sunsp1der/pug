from Opioid2D.public.Node import Node

from pug.component import *

from pig.keyboard import *
from pig.editor.agui import KeyDropdown

class Keys_Velocity( Component):
    """Control object velocity with keys for up, down, left, right."""
    #component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['velocity_x', 'Horizontal velocity set by up and down keys'],
            ['velocity_y', 'Vertical velocity set by left and right keys'],
            ['up_key', KeyDropdown, 
                    {'doc':'Press this key to set objects upward velocity'}],
            ['down_key', KeyDropdown, 
                    {'doc':'Press this key to set objects downward velocity'}],
            ['left_key', KeyDropdown, 
                    {'doc':'Press this key to set objects leftward velocity'}],
            ['right_key', KeyDropdown, 
                    {'doc':'Press this key to set objects rightward velocity'}],
            ]
    #defaults
    velocity_x = 50
    velocity_y = 50
    up_key = keys["UP"]
    down_key = keys["DOWN"]
    left_key = keys["LEFT"]
    right_key = keys["RIGHT"]
                
    @component_method
    def on_added_to_scene(self, scene):
        """Set keys when object is added to scene"""
        scene.register_key_down( self.down_key, 0, self.move_key, 
                                 0, self.velocity_y)
        scene.register_key_down( self.up_key, 0, self.move_key, 
                                 0, -self.velocity_y)
        scene.register_key_down( self.left_key, 0, self.move_key, 
                                 -self.velocity_x, 0)
        scene.register_key_down( self.right_key, 0, self.move_key, 
                                 self.velocity_x, 0)
        scene.register_key_up( self.down_key, 0, self.move_key, 
                                 0, -self.velocity_y)
        scene.register_key_up( self.up_key, 0, self.move_key, 
                                 0, self.velocity_y)
        scene.register_key_up( self.left_key, 0, self.move_key, 
                                 self.velocity_x, 0)
        scene.register_key_up( self.right_key, 0, self.move_key, 
                                 -self.velocity_x, 0)
        
    def move_key(self, x_delta, y_delta):
        self.owner.velocity += (x_delta, y_delta)
                
register_component( Keys_Velocity)

