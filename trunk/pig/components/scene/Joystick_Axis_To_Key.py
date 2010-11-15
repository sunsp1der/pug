from pug.component import *

from pig import PigScene
from pig.keyboard import keys
from pig.editor.agui import KeyDropdown

class Joystick_Axis_To_Key( Component):
    """Convert joystick axis movement to simulate keyboard key presses. This
component requires the Joystick_Input component.

This component has two axes on it because most physical sticks have left-right
and up-down information.

To see the events being sent by the joystick, look at the console output of the 
Joystick_Input component with test_mode set to True.   
"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [PigScene]
    # attributes:   
    _field_list = [
        ['left_key', KeyDropdown, 
                {'doc':'Key to simulate for negative x axis'}],
        ['right_key', KeyDropdown, 
                {'doc':'Key to simulate for positive x axis'}],
        ['up_key', KeyDropdown, 
                {'doc':'Key to simulate for negative y axis'}],
        ['down_key', KeyDropdown, 
                {'doc':'Key to simulate for positive y axis'}],
        ['joystick_id',"The joystick's ID number (event info: 'joy')"],
        ['x_axis_id',"The x axis ID number (event info: 'axis')"],
        ['y_axis_id',"The y axis ID number (event info: 'axis')"],
        ['threshold',
                "The value that the axis must pass to simulate a key press"]
        ]
    # defaults
    left_key = 'J'
    right_key = 'L'
    up_key = 'I'
    down_key = 'K'
    joystick_id = 0
    x_axis_id = 0
    y_axis_id = 1
    threshold = 0.5
    
    x_state = y_state = 0
       
    @component_method
    def handle_joyaxismotion( self, event):
        if event.joy != self.joystick_id:
            return
        if event.axis == self.x_axis_id:
            k = (self.left_key, self.right_key)
            state = self.x_state
            self.x_state = event.value
        elif event.axis == self.y_axis_id:
            k = (self.up_key, self.down_key)
            state = self.y_state
            self.y_state = event.value
        value = event.value
        threshold = self.threshold
        if value < -threshold:
            self.owner.do_key_callbacks( keys[k[0]])
            if state > threshold:
                self.owner.do_key_callbacks( keys[k[1]], keydict = "KEYUP")
        elif value > threshold:
            self.owner.do_key_callbacks( keys[k[1]])
            if state < -threshold:
                self.owner.do_key_callbacks( keys[k[0]], keydict = "KEYUP")
        elif state > threshold:
            self.owner.do_key_callbacks( keys[k[1]], keydict = "KEYUP")
        elif state < -threshold:
            self.owner.do_key_callbacks( keys[k[0]], keydict = "KEYUP")
        
        
    @component_method
    def register_key_down( self, key, fn, *args, **kwargs):
        "Check axis state when keys are registered"
        # if we don't do this we can get key up messages with no corresponding
        # key down
        if key in [self.left_key, self.right_key, self.up_key, self.down_key]:
            stick = self.owner.get_joystick(self.joystick_id)
            x_axis = stick.get_axis(self.x_axis_id)
            y_axis = stick.get_axis(self.y_axis_id)
            threshold = self.threshold
            if (key == self.left_key and x_axis < -threshold):
                fn(*args, **kwargs)
            if key == self.right_key and x_axis > threshold:
                fn(*args, **kwargs)
            if key == self.up_key and y_axis < -threshold:
                fn(*args, **kwargs)
            if key == self.down_key and y_axis > -threshold:
                fn(*args, **kwargs)
                    
                
                
                
    
register_component( Joystick_Axis_To_Key)
    