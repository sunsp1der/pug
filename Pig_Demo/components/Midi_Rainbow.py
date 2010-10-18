import colorsys

from Opioid2D.public.Node import Node

from pug.component import register_component, component_method

from pig.components import Spawn_On_Midi

class Midi_Rainbow( Spawn_On_Midi):
    """Object spawns on midi key press. Color of spawned object is determined by
which keys are currently pressed."""
    #component_info
    _set = 'pig_demo'
    _type = 'midi'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['spectrum_range', 'Range of midi keys for one full rainbow'],
            ] + Spawn_On_Midi._field_list
    # defaults
    spectrum_range = (48, 59)
    
    @component_method                
    def on_spawn( self, obj, component):
        # hue is a number from 0-1 representing color
        if not self.held_keys:
            return
        avg_key = sum(self.held_keys) / float(len(self.held_keys))
        diff = self.spectrum_range[1] - self.spectrum_range[0]
        hue = ((avg_key - self.spectrum_range[1]) % diff) / float(diff)        
        obj.color = colorsys.hsv_to_rgb( hue, 1, 1)

register_component( Midi_Rainbow)