"""Joystick_Input.py

This component adds joystick input functionality to a scene. It is an example of
how to add a whole new input device to a Scene.
"""
from pygame import joystick

from pug.component import *

from pig import Scene

class Joystick_Input( Component):
    """Activate joystick input. To convert joystick input to keys, use the
Joystick_To_Keys component.

This component adds a new function to scene:
get_joystick(id)->returns a pygame joystick object

To respond to joystick events, create the following methods in your scene:
handle_joybuttondown( event): event has joy (joystick #) and button (button #)
handle_joybuttonup( event): same as above
handle_joyaxismotion( event): event has joy, value (0-1) and axis (0=x, 1=y)
"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Scene]
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
                print 'Joystick_Input enabled joystick #' + str(x) + \
                                                        ': ' + j.get_name()
            self.joystick.append(j)
        if not joystick.get_count():
            if self.test_mode:
                print 'Joystick_Input: No Joysticks to Initialize'
            
        if self.test_mode:
            # create a mini component because we don't want to slow down
            # joystick response unless we're in test_mode
            class Joystick_Test_Component( Component):
                @component_method
                def handle_joybuttondown(self, event):
                    print event
                @component_method
                def handle_joybuttonup(self, event):
                    print event
                @component_method
                def handle_joyaxismotion(self, event):
                    print event
            self.owner.components.add(Joystick_Test_Component())

    @component_method
    def get_joystick(self, id):
        "Return the pygame joystick object with the given id."
        try:
            return self.joystick[id]
        except:
            return None

register_component( Joystick_Input)
