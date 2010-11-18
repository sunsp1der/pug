import os

import Opioid2D
from Opioid2D.public.Node import Node

from pug import Filename, Dropdown
from pug.component import *

from pig.components.behavior.Animate_Grid import Animate_Grid
from pig.components.controls.Key_Direction_Controls import \
                                                        Key_Direction_Controls

class Key_Animate_Direction( Animate_Grid, Key_Direction_Controls):
    """Control object velocity with up, down, left, right keys. Uses a set of 
animation or single images stored in a file that contains multiple frames.
"""
    #component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    # separate these to make derived components easier to write
    _field_list = Animate_Grid._grid_list + \
            [['fps','Frames per second'],
             ['up_frames',
                    'List of frame numbers and/or tuples in the ' +\
                    'range form ([start], stop, [step])'],
             ['upright_frames',
                    'List of frame numbers and/or tuples in the ' +\
                    'range form ([start], stop, [step])'],
             ['right_frames',
                    'List of frame numbers and/or tuples in the ' +\
                    'range form ([start], stop, [step])'],
             ['downright_frames',
                    'List of frame numbers and/or tuples in the ' +\
                    'range form ([start], stop, [step])'],
             ['down_frames',
                    'List of frame numbers and/or tuples in the ' +\
                    'range form ([start], stop, [step])'],
             ['downleft_frames',
                    'List of frame numbers and/or tuples in the ' +\
                    'range form ([start], stop, [step])'],
             ['left_frames',
                    'List of frame numbers and/or tuples in the ' +\
                    'range form ([start], stop, [step])'],
             ['upleft_frames',
                    'List of frame numbers and/or tuples in the ' +\
                    'range form ([start], stop, [step])'],
             ] + \
            Key_Direction_Controls._field_list 

    #defaults
    rotate = False
    up_frames = upright_frames = right_frames = downright_frames = down_frames\
            = downleft_frames = left_frames = upleft_frames = (0,1) 
            
    dir = None
    framedict = {}
    image_sprite = None 
    
    @component_method            
    def on_added_to_scene(self):
        Key_Direction_Controls.on_added_to_scene(self)
        (Opioid2D.Delay(0) + Opioid2D.CallFunc(self.do_load_frames)).do()
        
    def do_load_frames(self):
        self.load_frames()
        self.change_velocity(0,1)
        self.owner.velocity = (0,0)
             
    def load_frames(self):
        dirs = ['up_frames','upright_frames','right_frames','downright_frames',
                'down_frames','downleft_frames','left_frames','upleft_frames']
        for dir in dirs:
            try:
                self._frame_sequence = getattr(self, dir)
            except:
                continue
            self.framedict[dir] = self.get_frame_images() 
        
    def change_velocity(self, x_change, y_change):
        Key_Direction_Controls.change_velocity(self, x_change, y_change)
        vx, vy = self.owner.velocity
        dir =  None
        if vx > 0:
            if vy > 0:
                dir = "downright_frames"
            elif vy < 0:
                dir = "upright_frames"
            else:
                dir = "right_frames"
        elif vx < 0:
            if vy > 0:
                dir = "downleft_frames"
            elif vy < 0:
                dir = "upleft_frames"
            else:
                dir = "left_frames"
        elif vy > 0:
            dir = "down_frames"
        elif vy < 0:
            dir = "up_frames"
        if self.dir == dir or dir == None:
            return
        self.dir = dir
        self.frames = self.framedict[dir]
        try:
            self.anim_action.abort()
        except:
            pass
        action = Opioid2D.Animate(self.frames, fps=self.fps, 
                         mode=self.modes["Repeat"])
        if self.rotate:
            if self.image_sprite is None:
                self.image_sprite = Opioid2D.Sprite()
                self.image_sprite.attach_to(self.owner)
                self.owner.image = self.frames[0]
                self.owner.alpha = 0
            image_sprite = self.image_sprite
            image_sprite.rotation = -self.owner.rotation
        else:
            image_sprite = self.owner
        self.anim_action = action.do(image_sprite)
            
                
    def do_set_animation(self):
        self._frame_sequence = self.up_frames
        Animate_Grid.do_set_animation(self)

register_component( Key_Animate_Direction)
