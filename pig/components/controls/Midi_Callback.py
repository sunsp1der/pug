"Midi_Callback.py"
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
This component keeps track of currently on notes in the on_notes set.
"""
    # component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes:   
    _field_list = [
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
        self.k_info += [scene.register_key_down( keys["MIDI"], self.midi_event)]
        self.on_notes = {}
            
    def midi_event(self, event):
        if not event.channel in range(*self.channel_range):
            return
        if not event.data1 in range(*self.key_range):
            return
        if event.command == "NOTE_ON":
            try:
                self.on_notes[event.channel].add(event.data1)
            except:
                self.on_notes[event.channel] = set([event.data1])
        elif event.command == "NOTE_OFF":
            try:
                self.on_notes[event.channel].discard(event.data1)
            except:
                pass
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
        
       
