"""Midi_Input.py

This component adds midi input functionality to a scene. It is an example of
how to add a whole new input device to a Scene.
"""
import pygame.midi

from Opioid2D import RealTickFunc

from pug.component import *

from pig import Scene
from pig.keyboard import keys

class Midi_Input( Component):
    """Process input from a midi instrument

To register for midi events, call scene.register_key_down with the key MIDI_#
where # is the input_id (use pygame.midi.get_default_input_id to get default).
Registered callbacks will get ALL midi events for that input_id, with the midi
event itself as the first argument.
This component adds a function to the base scene:
    get_midi_state( )->midistate object

The midistate object contains the following attributes
    instruments = {} # {channel: current instrument}
    on_notes = {} # {channel: set(currently on notes)}
    other = {} # {channel: {command: (data1, data2), controller:data2}}    
"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Scene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['input_id', 'The midi input id. -1 uses default.'],
            ['test_mode', 'If True, prints all midi events to the console'],
            ['track_info', 
        'If True, track notes, controllers, and instruments in self.midi_state']
            ]
    #defaults
    input_id = -1
    test_mode = False
    track_info = False
    
    midi_state = None
        
    @component_method
    def on_start(self):
        "Initialize midi input"
        self.midi_state = midistate()
        try:
            pygame.midi.quit()
            pygame.midi.init()
            if self.input_id == -1:
                self.input_id = pygame.midi.get_default_input_id()
                if self.input_id == -1:
                    print "Midi_Input.on_start: No midi device available"
                    self.enabled = False
                    return
            if self.test_mode:
                print "Midi_Input Device List:"
                self.print_device_info()
                print "Midi_Input using device",self.input_id,"\n   ",
                self.print_device_info(self.input_id)
                
        except:
            print "Midi_Input.on_start: Midi input initialization error"
            self.enabled = False
            return
        try:
            self.input = pygame.midi.Input( self.input_id)
        except:
            print "Midi_Input.on_start: Midi port error!"
            self.enabled = False
            return
        self.tick_action = RealTickFunc(self.get_midi).do()
        
    def print_device_info( self, id=None):
        if id is None:
            ids = range( pygame.midi.get_count() )
        else:
            ids = [id]
        for i in ids:
            r = pygame.midi.get_device_info(i)
            (interf, name, input, output, opened) = r
    
            in_out = ""
            if input:
                in_out = "(input)"
            if output:
                in_out = "(output)"
    
            print ("%2i: interface :%s:, name :%s:, opened :%s:  %s" %
                   (i, interf, name, opened, in_out))        
        
    @component_method        
    def get_midi_state(self):
        return self.midi_state
    
    def get_midi(self):
        if self.input.poll():
            midi_events = self.input.read(64)
            pygame_events = self.midi_state.midis2events(midi_events, 
                                                         self.input_id)
            for event in pygame_events:
                if self.track_info:
                    self.midi_state.process_event(event)
                self.do_callbacks( event)
                if self.test_mode:
                    print event
                    
    def do_callbacks(self, ev):
        self.owner.do_key_callbacks( keys["MIDI"], a=(ev,))
                        
register_component( Midi_Input)

# The following is a midi utility object
class midistate():
    def __init__(self, track_state = True):
        self.instruments = {} # channel: instrument
        self.on_notes = {} # channel: set(on_notes)
        self.other = {} # channel: {controller: (data1, data2)}
        self.track_state = track_state

    def note_on(self, channel, note):
        try:
            self.on_notes[channel].add(note)
        except:
            self.on_notes[channel] = set([note])
    
    def note_off(self, channel, note):
        try:
            self.on_notes[channel].discard(note)
        except:
            self.on_notes[channel] = set()
            
    def process_event(self, e):
        if not self.track_state:
            return
        if e.command == "NOTE_ON":
            self.note_on( e.channel, e.data1)
        elif e.command == "NOTE_OFF":
            self.note_off( e.channel, e.data1)
        elif e.command == "PROGRAM_CHANGE":
            self.instruments[e.channel] = e.data1
        elif e.command == "CONTROLLER_CHANGE":
            try:
                self.other[e.channel][e.data1] =  e.data2
            except:
                self.other[e.channel] = {e.data1:e.data2}
        else:
            try:
                self.other[e.channel][e.command] = (e.data1,e.data2)
            except:
                self.other[e.channel] = {e.command:(e.data1,e.data2)}            

    def midis2events(self, midis, device_id, convert_note_off=True):
        """converts midi events to pygame events
        pygame.midi.midis2events(midis, device_id): return [Event, ...]
        
        argument convert_note_off: if True, NOTE_ON at 0 velocity converted to
                                    NOTE_OFF
    
        Takes a sequence of midi events and returns list of pygame events.
        """
        evs = []
        for midi in midis:            
            ((status,data1,data2,data3),timestamp) = midi
            if status == 0xFF:
                # pygame doesn't seem to get these, so I didn't decode
                command =  "META"
                channel = None
            else:
                try:
                    command = COMMANDS[ (status & 0x70) >> 4]
                    if data2 == 0 and command == "NOTE_ON" and convert_note_off:
                        command = "NOTE_OFF"
                except:
                    command = status & 0x70
                
                channel = status & 0x0F
            e = pygame.event.Event(pygame.midi.MIDIIN,
                                   status=status,
                                   command=command,
                                   channel=channel,
                                   data1=data1,
                                   data2=data2,
                                   timestamp=timestamp,
                                   device_id = device_id)
            evs.append( e )
        return evs

# Incomplete listing:
COMMANDS = {0: "NOTE_OFF",
            1: "NOTE_ON",
            2: "KEY_AFTER_TOUCH",
            3: "CONTROLLER_CHANGE",
            4: "PROGRAM_CHANGE",
            5: "CHANNEL_AFTER_TOUCH",
            6: "PITCH_BEND"}
# Incomplete listing: this is the key to CONTROLLER_CHANGE events data1
CONTROLLER_CHANGES = {1: "MOD WHEEL",
                      2: "BREATH",
                      4: "FOOT",
                      5: "PORTAMENTO",
                      6: "DATA",
                      7: "VOLUME",
                      10: "PAN",
                      }

