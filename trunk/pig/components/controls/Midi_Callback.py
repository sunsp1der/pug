"Midi_Callback.py"
import pygame.midi

from Opioid2D.public.Node import Node

from pug.component import *

from pig.keyboard import keys
from pig.PigDirector import PigDirector

class Midi_Callback( Component):
    """Owner receives midi events. Scene must have the Midi_Input component.
    
This component gives its owner a new callback:
    on_midi_event(event)
Derived components can use this to react to events.
Event contains raw midi data 'status', 'data1', and 'data2' as well as parsed
data 'command' and 'channel'. The main commands received are: NOTE_ON, NOTE_OFF,
CONTROLLER_CHANGE, and PROGRAM_CHANGE.
You can also check ongoing midi state using scene.get_midi_state() (see 
Midi_Input for more info)
"""
    # component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ['input_id', 'The midi input id. -1 uses default.'], 
        ['key_range', 'The range of midi keys to respond to'],
        ['channel_range', "The range of midi channels to respond to"],                  
        ]
    input_id = -1
    key_range = (0, 100)
    channel_range = (0,16)
    rapid_fire = True

    interval_complete = True  
    
    @component_method
    def on_scene_start(self, scene):
        "Set spawn key and setup the spawner"
        self.k_info = []
        if self.input_id == -1:
            default = pygame.midi.get_default_input_id()
            if default == -1:
                print "Midi_Callback: No midi device available"
                self.enabled = False
                return
            key_id =  keys["MIDI_0"] + default
        else:
            key_id = keys["MIDI_0"] + self.input_id
        self.k_info += [scene.register_key_down( key_id, self.midi_event)]
            
    def midi_event(self, event):
        if not event.channel in range(*self.channel_range):
            return
        if not event.data1 in range(*self.key_range):
            return
        self.owner.on_midi_event(event)
        
    @component_method
    def on_midi_event(self, event):
        pass
    
    @component_method
    def on_destroy(self):
        """unregister keys when component is destroyed"""
        scene = PigDirector.scene
        for k in self.k_info:
            scene.unregister_key(k)
        self.k_info = []
 
register_component( Midi_Callback)
        
       
