from Opioid2D.public.Node import Node

from pug.component import *

from pig.keyboard import *
from pig.editor.agui import KeyDropdown
from pig.PigDirector import PigDirector

class Key_Direction_Controls( Component):
    """Control object velocity with keys for up, down, left, right."""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['x_velocity', 'Horizontal velocity set by up and down keys'],
            ['y_velocity', 'Vertical velocity set by left and right keys'],
            ['rotate', 'Rotate object to face direction of movement'],
            ['up_key', KeyDropdown, 
                {'doc':"Press this key to set object's upward velocity"}],
            ['down_key', KeyDropdown, 
                {'doc':"Press this key to set object's downward velocity"}],
            ['left_key', KeyDropdown, 
                {'doc':"Press this key to set object's leftward velocity"}],
            ['right_key', KeyDropdown, 
                {'doc':"Press this key to set object's rightward velocity"}],
            ]
    #defaults
    x_velocity = 100
    y_velocity = 100
    rotate = True 
    up_key = keys["UP"]
    down_key = keys["DOWN"]
    left_key = keys["LEFT"]
    right_key = keys["RIGHT"]
    
                
    @component_method
    def on_added_to_scene(self, scene):
        """Set keys when object is added to scene"""
        self.k_info = range(8) #unregister information
        self.k_info[0] = scene.register_key_down( self.down_key, 
                                    self.change_velocity, 0, self.y_velocity)
        self.k_info[1] = scene.register_key_down( self.up_key, 
                                    self.change_velocity, 0, -self.y_velocity)
        self.k_info[2] = scene.register_key_down( self.left_key, 
                                    self.change_velocity, -self.x_velocity, 0)
        self.k_info[3] = scene.register_key_down( self.right_key, 
                                    self.change_velocity, self.x_velocity, 0)
        self.k_info[4] = scene.register_key_up( self.down_key, 
                                    self.change_velocity, 0, -self.y_velocity)
        self.k_info[5] = scene.register_key_up( self.up_key, 
                                    self.change_velocity, 0, self.y_velocity)
        self.k_info[6] = scene.register_key_up( self.left_key, 
                                    self.change_velocity, self.x_velocity, 0)
        self.k_info[7] = scene.register_key_up( self.right_key, 
                                    self.change_velocity, -self.x_velocity, 0)
        
    def change_velocity(self, x_change, y_change):
        """Change owner's velocity"""
        self.owner.velocity += (x_change, y_change)
        if self.rotate and self.owner.velocity.length: 
            self.owner.rotation = self.owner.velocity.direction        
    
    @component_method
    def on_destroy(self):
        """unregister keys when component is destroyed"""
        scene = PigDirector.scene
        for info in self.k_info:
            scene.unregister_key(info)
            
register_component( Key_Direction_Controls)
