import os

import Opioid2D
from Opioid2D.public.Node import Node

from pug import ImageBrowser, Dropdown
from pug.component import *

from pig.editor.util import _fl_art_types
from pig.animation import get_grid_sequence_frames
from pig.components.behavior.Animate_Folder import Animate_Folder

class Animate_Grid(Animate_Folder):
    """This object is an animation. Grid animations are stored in files that 
contain multiple frames.
"""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    # separate these to make derived components easier to write
    _grid_list = [ 
            ['file',ImageBrowser,{'doc':'Grid animation file', 
                                      'subfolder':'art', 'filter':_fl_art_types,
                                      'allow_delete':True 
                                     }],
            ['grid_width','Width of one grid unit in file'],
            ['grid_height','Height of one grid unit in file'],
            ]
    _frame_list = [
            ['frame_sequence', 
                     'List of frame numbers and/or tuples in the ' +\
                     'range form ([start], stop, [step])'],
            ]
    _field_list = _grid_list + _frame_list
    _field_list += Animate_Folder._animate_list
    #defaults
    _grid_width = 64
    _grid_height = 64
    _frame_sequence = [(0,6)]
    
    action = None
    
    def get_frame_images(self):
        info = (self.file, self.grid_width, self.grid_height, 
                self._frame_sequence)
        if self.last_frame_info == info:
            return self.frames
        frames = get_grid_sequence_frames( *info)
        self.last_frame_info = info
        return frames
    
    file = property(lambda s: s.get_anim_attr("_animation"),
                          lambda s, val: s.set_anim_attr("_animation", val) )
    grid_width = property(lambda s: s.get_anim_attr("_grid_width"),
                          lambda s, val: s.set_anim_attr("_grid_width", val) )
    grid_height = property(lambda s: s.get_anim_attr("_grid_height"),
                          lambda s, val: s.set_anim_attr("_grid_height", val) )
    frame_sequence = property(lambda s: s.get_anim_attr("_frame_sequence"),
                        lambda s, val: s.set_anim_attr("_frame_sequence", val) )
    
register_component( Animate_Grid)
