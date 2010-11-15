from pug.component import *

from pig import PigScene
from pig.keyboard import keys
from pig.editor.agui import KeyDropdown

class Joystick_Button_To_Key( Component):
    """Convert joystick button presses to simulate keyboard key presses. This
component requires the Joystick_Input component.

To see the events being sent by the joystick, look at the console output of the 
Joystick_Input component with test_mode set to True.   
"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [PigScene]
    # attributes:   
    _field_list = [
        ['button_0', KeyDropdown, 
            {'doc':'Key to simulate when button 0 is pressed'}],
        ['button_1', KeyDropdown, 
            {'doc':'Key to simulate when button 1 is pressed'}],
        ['button_2', KeyDropdown, 
            {'doc':'Key to simulate when button 2 is pressed'}],
        ['button_3', KeyDropdown, 
            {'doc':'Key to simulate when button 3 is pressed'}],
        ['button_4', KeyDropdown, 
            {'doc':'Key to simulate when button 4 is pressed'}],
        ['button_5', KeyDropdown, 
            {'doc':'Key to simulate when button 5 is pressed'}],
        ['button_6', KeyDropdown, 
            {'doc':'Key to simulate when button 6 is pressed'}],
        ['button_7', KeyDropdown, 
            {'doc':'Key to simulate when button 7 is pressed'}],
        ['button_8', KeyDropdown, 
            {'doc':'Key to simulate when button 8 is pressed'}],
        ['button_9', KeyDropdown, 
            {'doc':'Key to simulate when button 9 is pressed'}],
        ['button_10', KeyDropdown, 
            {'doc':'Key to simulate when button 10 is pressed'}],
        ['button_11', KeyDropdown, 
            {'doc':'Key to simulate when button 11 is pressed'}],
        ]
    # defaults
    button_0 = "SPACE"
    button_1 = "SPACE"
    button_2 = "SPACE"
    button_3 = "SPACE"
    button_4 = "SPACE"
    button_5 = "SPACE"
    button_6 = "SPACE"
    button_7 = "SPACE"
    button_8 = "SPACE"
    button_9 = "SPACE"
    button_10 = "SPACE"
    button_11 = "SPACE"
       
    @component_method
    def handle_joybuttondown( self, event):
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
                    
                
                
                
    
register_component( Joystick_Button_To_Key)
    