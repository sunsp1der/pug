from Opioid2D.public.Node import Node

from pug.component import *

from pig.keyboard import *
from pig.editor.agui import KeyDropdown
from pig.PigDirector import PigDirector
from pig.components.behavior.Forward_Motion import Forward_Motion
from pig.components.controls.Key_Direction_Controls import \
                                                        Key_Direction_Controls

class Key_Drive_Controls( Forward_Motion, Key_Direction_Controls):
    """Keys for forward, backward, and rotate left/right"""
    #component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = Forward_Motion._field_list[:]
    _field_list += [
            ['friction','0-1 velocity multiplier.\n'+\
                        'Only works if accelerate is True'],                    
            ['rotation_speed', 'How fast object turns'],
            ['forward_key', KeyDropdown, 
                    {'doc':"Press this key to set this\n"+\
                            "object's forward velocity"}],
            ['backward_key', KeyDropdown, 
                    {'doc':"Press this key to set this\n"+\
                            "object's backward velocity"}],
            ['left_key', KeyDropdown, 
                    {'doc':"Press this key to set this object's\n"+\
                            "leftward rotation speed"}],
            ['right_key', KeyDropdown, 
                    {'doc':"Press this key to set this object's\n"+\
                            "rightward rotation speed"}],
            ]
    #defaults
    friction = 0.98
    speed = 200
    rotation_speed = 135
    forward_key = keys["I"]
    backward_key = keys["K"]
    left_key = keys["J"]
    right_key = keys["L"]
                
    acceleration = None # for Forward_Motion
    
    @component_method
    def on_added_to_scene(self, scene):
        """Set keys when object is added to scene"""
        self.k_info = range(8) #unregister information
        self.k_info[0] = scene.register_key_down( self.forward_key, 
                                    self.change_velocity, self.speed)
        self.k_info[1] = scene.register_key_down( self.backward_key, 
                                    self.change_velocity, -self.speed)
        self.k_info[2] = scene.register_key_down( self.right_key, 
                                    self.change_rotation, self.rotation_speed)
        self.k_info[3] = scene.register_key_down( self.left_key, 
                                    self.change_rotation, -self.rotation_speed)
        self.k_info[4] = scene.register_key_up( self.forward_key, 
                                    self.change_velocity, -self.speed)
        self.k_info[5] = scene.register_key_up( self.backward_key, 
                                    self.change_velocity, self.speed)
        self.k_info[6] = scene.register_key_up( self.right_key, 
                                    self.change_rotation, -self.rotation_speed)
        self.k_info[7] = scene.register_key_up( self.left_key, 
                                    self.change_rotation, self.rotation_speed)
        self.owner.friction = self.friction
        self.speed = 0 # our actual starting speed
        
    def change_velocity(self, delta):
        self.speed += delta
        self.set_forward_motion()
        
    def change_rotation(self, delta):
        self.owner.rotation_speed += delta
        
    def on_destroy(self):
        Key_Direction_Controls.on_destroy(self)
        Forward_Motion.on_destroy(self)
                
register_component( Key_Drive_Controls)

