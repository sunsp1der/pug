"Spawn_On_Midi.py"
import pygame.midi

from Opioid2D.public.Node import Node

from pug.component import component_method, register_component

from pig.keyboard import keys
from pig.actions import Delay, CallFunc
from pig.components.spawn.Spawner import Spawner
from pig.PigDirector import PigDirector

class Spawn_On_Midi( Spawner):
    """Owner spawns when Midi key pressed.
    
Derived components can use on_midi_event(event) to react to events"""
    # component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ['input_id', 'The midi input id. -1 uses default.'], 
        ['key_range', 'The range of midi keys to respond to'],                  
        ['rapid_fire', 'Holding down key spawns continuously'],
        ]
    _field_list += Spawner._field_list
    
    input_id = -1
    key_range = (0,200)
    rapid_fire = True

    interval_complete = True  
    
    @component_method
    def on_added_to_scene(self, scene):
        self.held_keys = set([])    
        self.setup_spawner()
    
    @component_method
    def on_scene_start(self, scene):
        "Set spawn key and setup the spawner"
        self.k_info = []
        if self.input_id == -1:
            default = pygame.midi.get_default_input_id()
            if default == -1:
                print "Spawn_On_Midi: No midi device available"
                self.enabled = False
                return
            key_id =  keys["MIDI_0"] + default
        else:
            key_id = keys["MIDI_0"] + self.input_id
        self.k_info += [scene.register_key_down( key_id, self.midi_event)]
            
    def midi_event(self, event):
        if not(event.data1 >= self.key_range[0] and \
               event.data1 <= self.key_range[1]):
            return
        try:
            self.on_midi_event(event)
        except:
            pass            
        if event.data2:
            if not self.held_keys:
                self.held_keys.add(event.data1)
                self.check_spawn()
            else:
                self.held_keys.add(event.data1)
        else:
            self.held_keys.discard(event.data1)
            if not self.held_keys:
                self.stop_spawning()
    
    def check_spawn(self, schedule_next=False):
        self.spawning = True
        if self.interval_complete:  
            # spawn_interval has completed          
            spawns = Spawner.check_spawn(self, schedule_next)
            if spawns:
                # we just spawned so we need to wait for interval again
                self.interval_complete = False
                # get next spawn_interval
                interval = self.get_next_spawn_wait()
                # set a timer to change interval_complete to True
                self.owner.do( Delay(interval) + CallFunc(self.set_complete, 
                                                          True))

    def set_complete(self, val):
        self.interval_complete = val
        if self.rapid_fire and self.owner and self.spawning:
            # when rapid_firing, we CAN shoot, so try to shoot!
            self.check_spawn()
            
    def stop_spawning(self):
        self.spawning = False

    @component_method
    def on_destroy(self):
        """unregister keys when component is destroyed"""
        scene = PigDirector.scene
        for k in self.k_info:
            scene.unregister_key(k)
        self.k_info = []
 
register_component( Spawn_On_Midi)
        
       
