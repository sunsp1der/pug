from pug.component import *

from pig import PigScene
from pig.keyboard import keys
from pig.editor.agui import KeyDropdown
from pig.components.controls.Midi_Callback import Midi_Callback

class Midi_To_Key( Midi_Callback):
    """Convert a range of midi keys to simulate a keyboard key press"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [PigScene]
    # attributes:   
    _field_list = [
        ['key', KeyDropdown, 
                {'doc': 'The key to simulate when midi event is received'}],
        ['do_key_up',"When no selected notes are on, do key up"],
        ]
    _field_list += Midi_Callback._field_list
    key = keys["SPACE"]
    do_key_up = True
    k_info = []
    
    @component_method
    def on_start(self):
        "Get the sound object and set it to play when key is pressed"
        Midi_Callback.on_scene_start(self, self.owner)
        
    def midi_event(self, event):
        has_on_note = self.has_on_note
        Midi_Callback.midi_event(self, event)
        if not has_on_note and self.has_on_note and self.do_key_up:
            # note on
            self.owner.do_key_callbacks( self.key)
        elif has_on_note and not self.has_on_note:
            # note off
            self.owner.do_key_callbacks( self.key, keydict="KEYUP")

    @component_method
    def exit(self):
        "Unregister key"
        self.on_destroy()
    
register_component( Midi_To_Key)
    