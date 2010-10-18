import pygame.midi

from Opioid2D import RealTickFunc

from pug.component import *

from pig import PigScene
from pig.PigDirector import PigDirector

class Midi_Input( Component):
    """Process input from a midi instrument

To register for midi events, call scene.register_key_down with the key MIDI_#
where # is the input_id (use pygame.midi.get_default_input_id to get default).
Registered callbacks will get ALL midi events for that input_id, with the midi
event itself as the first argument.
"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [PigScene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['input_id', 'The midi input id. -1 uses default.'],
            ]
    #defaults
    input_id = -1
        
    @component_method
    def on_start(self):
        pygame.midi.quit()
        pygame.midi.init()
        if self.input_id == -1:
            self.input_id = pygame.midi.get_default_input_id()
            if self.input_id == -1:
                print "Midi_Input.on_start: No midi device available"
                self.enabled = False
                return
        self.input = pygame.midi.Input( self.input_id)
        self.tick_action = RealTickFunc(self.get_midi).do()
        
    def get_midi(self):
        if self.input.poll():
            midi_events = self.input.read(64)
            pygame_events = pygame.midi.midis2events(midi_events, self.input_id)
            for event in pygame_events:
                self.do_callbacks( event)
                
    def do_callbacks(self, ev):
        dict = self.owner._key_down_dict
        fn_list = dict.get((0, 1100 + self.input_id), [])
        for fn_info in fn_list:
            fn_info[0](ev,*fn_info[1], **fn_info[2])
            # print ev # if you need to see what the event looks like
            
register_component( Midi_Input)