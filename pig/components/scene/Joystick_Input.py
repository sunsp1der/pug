"""Joystick_Input.py

This component adds joystick input functionality to a scene. It is an example of
how to add a whole new input device to a PigScene.
"""
from pygame import joystick

from pug.component import *

from pig import PigScene

class Joystick_Input( Component):
    """Activate joystick input. To convert joystick input to keys, use the
Joystick_To_Keys component.

To access the pygame joystick objects, use the joystick[] attribute of this 
component.

To respond to joystick events, create the following methods in your scene:
handle_joybuttondown( event): event has joy (joystick #) and button (button #)
handle_joybuttonup( event): same as above
handle_joyaxismotion( event): event has joy, value (0-1) and axis (0=x, 1=y)
"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [PigScene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['test_mode', 'If True, prints all joystick events to the console'],
            ]
    #defaults
    test_mode = False
    @component_method
    def on_start(self):
        "Initialize joysticks"
        self.joystick = []
        for x in range(joystick.get_count()):
            j = joystick.Joystick(x)
            j.init()
            if self.test_mode:
                print 'Joystick_Input enabled joystick: ' + j.get_name()
            self.joystick.append(j)
        if not joystick.get_count():
            if self.test_mode:
                print 'Joystick_Input: No Joysticks to Initialize'

register_component( Joystick_Input)
