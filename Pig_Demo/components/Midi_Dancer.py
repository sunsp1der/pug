import os

import Opioid2D
from Opioid2D.public.Node import Node

from pug import ImageBrowser, Dropdown
from pug.component import *

from pig.components.behavior.Animate_Grid import Animate_Grid
from pig.components.controls.Midi_Callback import Midi_Callback

class Midi_Dancer(Midi_Callback, Animate_Grid):
    #component_info
    _set = 'pig_demo'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    # separate these to make derived components easier to write
    _field_list = []
    _field_list += Animate_Grid._grid_list + Animate_Grid._frame_list
    _field_list += Midi_Callback._field_list
    _field_list += [['key_start','Midi key that shows frame zero.']]
    #defaults
    key_start = 0
    
    @component_method
    def on_added_to_scene(self, scene):
        self.owner.image = self.frames[0]
    
    @component_method
    def on_midi_event(self, event):
        if not self.frames:
            return
        count = len(self.frames)
        frame = (event.data1 - self.key_start) % count
        self.owner.image = self.frames[frame]
        
register_component( Midi_Dancer)
