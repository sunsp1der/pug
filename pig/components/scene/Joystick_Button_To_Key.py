from pygame.key import get_pressed

from pug.component import *

from pig import PigScene
from pig.keyboard import keys
from pig.editor.agui import KeyDropdown

class Joystick_Button_To_Key( Component):
    """Convert joystick button presses to simulate keyboard key presses. This
component requires the Joystick_Input component. Note that strange effects can
occur if both the joystick and keyboard are used simultaneously.

To see the events being sent by the joystick, look at the console output of the 
Joystick_Input component with test_mode set to True.   
"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [PigScene]
    # attributes:   
    _field_list = [
        ['joystick_id',"The joystick's ID number (event info: 'joy')"],                   
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
    joystick_id = 0
    button_0 = "SPACE"
    button_1 = None 
    button_2 = None
    button_3 = None
    button_4 = None
    button_5 = None
    button_6 = None
    button_7 = None
    button_8 = None
    button_9 = None
    button_10 = None
    button_11 = None
    
    def __init__( self, *a, **kw):
        self.downbuttons = {}
        Component.__init__( self, *a, **kw)
       
    @component_method
    def handle_joybuttondown( self, event):
        if event.joy != self.joystick_id:
            return
        key = keys[getattr(self, "button_" + str(event.button))]
        if key:
            self.owner.do_key_callbacks( key)
        
    @component_method
    def handle_joybuttonup( self, event):
        if event.joy != self.joystick_id:
            return
        key = keys[getattr(self, "button_" + str(event.button))]
        if key:
            self.owner.do_key_callbacks( key, keydict="KEYUP")
        
    @component_method
    def register_key_down( self, key, fn, *args, **kwargs):
        "Check axis state when keys are registered"
        # if we don't do this we can get key up messages with no corresponding
        # key down
        stick = self.owner.get_joystick(self.joystick_id)
        if not stick:
            return        
        n = 0
        for button in [self.button_0, self.button_1, self.button_2, 
                self.button_3, self.button_4, self.button_5, self.button_6, 
                self.button_7, self.button_8, self.button_9, self.button_10, 
                self.button_11]:
            if key == button and stick.get_button( n):
                fn( *args, **kwargs)
                return
            n += 1
    
register_component( Joystick_Button_To_Key)
    