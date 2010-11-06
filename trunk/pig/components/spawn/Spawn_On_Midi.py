"Spawn_On_Midi.py"
import colorsys

from Opioid2D.public.Node import Node

from pug.component import component_method, register_component

from pig.actions import Delay, CallFunc
from pig.components.spawn.Spawner import Spawner
from pig.components.controls.Midi_Callback import Midi_Callback
from pig.PigDirector import PigDirector

class Spawn_On_Midi( Midi_Callback, Spawner):
    """Owner spawns when Midi key pressed. Spawned objects can be tinted 
according to note played.
"""
    # component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes:   
    _field_list = Midi_Callback._field_list
    _field_list += [
        ['rapid_fire', 'Holding down key spawns continuously'],
        ['note_tint', 'Tint the spawned objects according to on notes'],
        ['spectrum_range', 'Range of midi keys for one full rainbow'],
        
        ]
    _field_list += Spawner._field_list
    
    rapid_fire = True
    note_tint = True
    spectrum_range = (48, 59)

    interval_complete = True  
    
    @component_method
    def on_added_to_scene(self, scene):
        self.setup_spawner()
       
    @component_method     
    def on_midi_event(self, event):
        if self.rapid_fire:
            if event.command == "NOTE_ON":
                self.check_spawn()
            elif event.command == "NOTE_OFF":
                stop = True
                for channel in range(*self.channel_range):
                    try:
                        on_notes = PigDirector.scene.get_midi_state().on_notes\
                                                                    [channel]
                    except KeyError:
                        continue                                                
                    if on_notes.intersection(range(*self.key_range)):
                        stop = False
                        break
                if stop:
                    self.stop_spawning()
        elif event.command == "NOTE_ON":
            self.check_spawn()    
    
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
            # when rapid_firing, we CAN spawn, so try to shoot!
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
        
    @component_method
    def on_spawn(self, obj, component):
        """Tint spawned objects according to notes held"""
        if not self.note_tint or not self.on_notes:
            return
        total = 0
        count = 0
        for notes in self.on_notes.itervalues():
            total += sum(notes)
            count += 1.0
        avg_key = total/count
        diff = self.spectrum_range[1] - self.spectrum_range[0]
        hue = ((avg_key - self.spectrum_range[1]) % diff) / float(diff)        
        obj.color = colorsys.hsv_to_rgb( hue, 1, 1)
 
register_component( Spawn_On_Midi)
        
       
