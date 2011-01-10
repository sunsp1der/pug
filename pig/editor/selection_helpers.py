from weakref import proxy
from math import sin, cos, radians

from pygame import Rect
import pygame.key

import wx

import Opioid2D
from Opioid2D.public.Node import Node
from Opioid2D import Mouse

from pig.PigDirector import PigDirector
from pig.editor.util import get_image_path
from pig.util import is_shift_down, is_ctrl_down, angle_to
from pig import PigSprite

wx = wx

_line_sprite_file = get_image_path("dot.png")
_handle_sprite_file = get_image_path("dot.png")
_empty_sprite_file = get_image_path("empty.png")

_HANDLE_SIZE = 6.0

class SelectBox():
    """SelectBox(): box that surrounds selected nodes
    
A selection box around a given rect. Contains dict 'lines' of line sprites whose
indexes are 'top', 'bottom', 'left', and 'right'. Also contains 'base' Sprite
which is invisible and sets the center of the object. And 'area' sprite which is
invisible and draggable.
 
Some day, this should use line primitives instead of stretched sprites. And even
handles for scaling and rotating.
"""
    rect = None
    drag_offset = (0,0)
    hotspot = None
    def __init__(self, node = None):
        """__init__( node=None)

node: any object containing a 'rect' attribute that is a pygame rect
"""
        self.graphicsManager = PigDirector.scene.state.graphicsManager
        base = SelectBoxBaseSprite() 
        area = SelectBoxAreaSprite()
        area.attach_to(base)
        area.position = (0,0)        
        self.base = base
        self.area = area
        self.area.box = proxy(self)
        self.rect = Rect([0,0,0,0])
        self.lines = {}
        self.handles = {}
        for side in ['left','right','top','bottom']:
            # edge lines
            line = SelectBoxLineSprite()
            line.attach_to(base)
            self.lines[side] = line
            # tool handles
            handle = SelectBoxHandleSprite()
            handle.attach_to(base)
            handle.id = side
            handle.box = proxy(self)
            self.handles[side] = handle
        for corner in ['top-left','top-right','bottom-left','bottom-right']:
            handle = SelectBoxHandleSprite()
            handle.attach_to(base)
            handle.id = corner
            handle.box = proxy(self)
            self.handles[corner] = handle 
        if node:
            self.surround_node( node)
            self.start_pulse()
    
    def on_drag_begin(self):
#        layer = PigDirector.scene.get_layer("__editor1__")
        node = self.get_node()
        layer = node.layer
        position = Opioid2D.Mouse.get_position()
        world_position = layer.convert_pos(position[0], position[1])
        if node:
            self.drag_offset = node.position - world_position
        else:
            self.drag_offset = (0,0)   
        
    def get_node(self):  
        boxDict = self.graphicsManager.boxDict
        for node, box in boxDict.iteritems():
            if box == self:
                return node
    node = property(get_node)
        
    def on_drag(self, node):
        layer = PigDirector.scene.get_layer("__editor1__")
        position = Opioid2D.Mouse.get_position()
        new_position = layer.convert_pos(position[0], position[1])\
                         + self.drag_offset
        node.position = new_position 
        self.surround_node( node)
        
    def on_rotate_begin(self, handle):
        self.orig_rot = self.node.rotation
        mouse_pos = Mouse.get_position()
        self.orig_angle = angle_to(self.node.position, mouse_pos)        
         
    def on_rotate(self, handle):
        mouse_pos = Mouse.get_position()
        angle = angle_to(self.node.position, mouse_pos)
        new_rotation = self.orig_rot + angle - self.orig_angle
        if is_shift_down():
            new_rotation = round(new_rotation / 15.0) * 15
        new_rotation = round(new_rotation, 1) 
        self.node.rotation = new_rotation
        handle.position = (0,0)
        self.surround_node(force=True)                        
        
    def on_scale_begin(self, handle):
        node = self.node  
        self.drag_from = Mouse.get_position()   
        self.orig_rect = node.rect.size  
        self.orig_scale = tuple(node.scale)
        self.orig_position = Opioid2D.Vector(self.node.position[0],
                                             self.node.position[1])
  
    def on_scale(self, handle):
        node = self.get_node()
        mouse_pos = Mouse.get_position()
        delta = Opioid2D.Vector(mouse_pos[0] - self.drag_from[0],
                                mouse_pos[1] - self.drag_from[1])
        movedir = Opioid2D.Vector() # adjust sprite hotspot
        delta.direction -= node.rotation
        location = handle.id
        # calculate scale changes
        if 'left' in location: 
            xchange = -delta[0]
            movedir[0] = -1 + (self.hotspot[0] - 0.5) * 2
        elif 'right' in location:
            xchange = delta[0] 
            movedir[0] = 1 + (self.hotspot[0] - 0.5) * 2
        else:
            handle.position[0] = xchange = 0
        if 'top' in location: 
            ychange = -delta[1]
            movedir[1] = -1 + (self.hotspot[1] - 0.5) * 2
        elif 'bottom' in location:
            ychange = delta[1]
            movedir[1] = 1 + (self.hotspot[1] - 0.5) * 2
        else: 
            handle.position[1] = ychange = 0
        xscale = self.orig_scale[0] * (self.orig_rect[0] + xchange)\
                                            / self.orig_rect[0]
        yscale = self.orig_scale[1] * (self.orig_rect[1] + ychange)\
                                            / self.orig_rect[1]
        # check proportional scale
        if is_shift_down():
            if location in ['top', 'bottom'] or \
                        (xscale/self.orig_scale[0] > yscale/self.orig_scale[1]\
                            and not location in ['left','right']):
                xscale = self.orig_scale[0] * abs(yscale)/self.orig_scale[1]
            else:
                yscale = self.orig_scale[1] * abs(xscale)/self.orig_scale[0]
        xscale = round(xscale,3)
        yscale = round(yscale,3)
        node.scale = (xscale, yscale)
        # reposition sprite
        movevector = Opioid2D.Vector()
        movevector[0] = movedir[0] * (node.rect.width - self.orig_rect[0]) \
                         / 2.0
        movevector[1] = movedir[1] * (node.rect.height - self.orig_rect[1]) \
                        / 2.0 
        movevector.direction += node.rotation
        print node.position
        node.position = self.orig_position + movevector
        print node.position
        # set lines and handles
        self.surround_node(force=True)                
        
    def start_pulse(self):
        pulse = Opioid2D.ColorFade((0.15,0.2,0.25,1), 1.2,Opioid2D.PingPongMode)
#        pulse = Opioid2D.AlphaFade(0.2, 1.2, Opioid2D.PingPongMode)
        for sprite in self.lines.itervalues():
            sprite.do(pulse)
#        for sprite in self.handles.itervalues():
#            sprite.do(pulse)
            
    def __del__(self):
        self.base.delete()
        self.area.delete()
        for line in self.lines.itervalues():
            line.delete()
        for handle in self.handles.itervalues():
            handle.delete()

    def surround_node(self, node=None, force=False):
        if node is None:
            node = self.get_node()
        try:
            hotspot = (node.image._cObj.hotspot.x, node.image._cObj.hotspot.y)
            rect = node._get_rect()
        except:
            return
        if self.rect == rect and self.hotspot == hotspot and \
                self.base.rotation == node.rotation and not force:
            return
        self.hotspot = hotspot
        self.rect = rect
        # match hotspot
        self.area.position[0] = rect.width * (0.5 - hotspot[0])
        self.area.position[1] = rect.height * (0.5 - hotspot[1])
        #match rotation
        self.base.rotation = node.rotation
        # match positions
        position = (node.position.x, node.position.y)
        self.rect.center = position
        self.base.position = position
        # match size
        line = self.lines['left']
        line.position = self.area.position + (rect.width * -0.5 - 1, 0.5)
        line.scale = (1,rect.height+2)
        
        line = self.lines['right']
        line.position = self.area.position + (rect.width * 0.5 + 1, 0.5)
        line.scale = (1,rect.height+2)
        
        line = self.lines['top']
        line.position = self.area.position + (0, rect.height * -0.5 - 1)
        line.scale = (rect.width + 3, 1)
        
        line = self.lines['bottom']
        line.position = self.area.position + (0, rect.height * 0.5 + 1)
        line.scale = (rect.width + 1, 1)
        
        x_offset = y_offset = _HANDLE_SIZE / 2
        if node.scale.x < 0:
            x_offset *= -1
        if node.scale.y < 0:
            y_offset *= -1
        for location, handle in self.handles.iteritems():
#            if not handle.dragging:
            handle.position = self.area.position
            if 'top' in location: 
                handle.position.y = self.lines['top'].position[1]\
                                                   - y_offset - 0.5
            elif 'bottom' in location:                    
                handle.position.y = self.lines['bottom'].position[1]\
                                                   + y_offset
            if 'left' in location:
                handle.position.x = self.lines['left'].position[0]\
                                                    - x_offset - 0.5
            elif 'right' in location:
                handle.position.x = self.lines['right'].position[0]\
                                                    + x_offset
        self.area.scale = (rect.width, rect.height)
        
class SelectBoxBaseSprite( PigSprite):
    layer = "__editor1__"
    auto_scene_register = False

class SelectBoxLineSprite( SelectBoxBaseSprite):
    color = (0.7,0.75,0.8,1)
    image = _line_sprite_file
    
class SelectBoxAreaSprite( SelectBoxBaseSprite):
    image = _empty_sprite_file
    draggable = True
    dragging = False
    def on_create(self):
        self.graphicsManager = PigDirector.scene.state.graphicsManager
        self.mouse_register("single")
        
    def on_drag_begin(self):
        self.box.on_drag_begin()
        PigDirector.scene.state.selectOnUp = None
        self.dragging = True

    def on_drag_end(self):
        self.dragging = False
        PigDirector.scene.state.selectOnUp = None
        self.graphicsManager.update_selection_boxes()
        wx.CallAfter(wx.GetApp().selection_refresh)
        
class SelectBoxHandleSprite( SelectBoxBaseSprite):
    layer = "__editor2__"
    image = _handle_sprite_file
    draggable = True
    dragging = False
    color = (0.7,0.75,0.8,1)
    tick_action = None
    def on_create(self):
        self.scale = (_HANDLE_SIZE, _HANDLE_SIZE)
        self.state = PigDirector.scene.state.graphicsManager
        self.graphicsManager = PigDirector.scene.state.graphicsManager
        self.mouse_register("single")

    def on_press(self):
        PigDirector.scene.state.mouse_locked_by = self
        
    def on_enter(self):
        if not PigDirector.scene.state.mouse_locked_by and \
                    pygame.key.get_focused():
            self.tick_action = Opioid2D.TickFunc( self.test_cursor).do()
    
    def test_cursor(self):
        if self.dragging:
            return
        if is_ctrl_down():
            #TODO: ctrl can't be tested when window doesn't have focus:(
            Mouse.cursor = Opioid2D.ResourceManager.get_image( 
                                            get_image_path("rotate.png"),
                                            (0.28,0.16))
        else:
            Mouse.cursor = Opioid2D.ResourceManager.get_image( 
                                            get_image_path("scale.png"),
                                            (0,0))
            
    def on_exit(self):
        if not self.dragging and not PigDirector.scene.state.mouse_locked_by:
            if self.tick_action:
                self.tick_action.abort()
            Mouse.cursor = Opioid2D.HWCursor.arrow
                
    def on_drag_begin(self):
        PigDirector.scene.state.selectOnUp = None
        self.dragging = True
        if is_ctrl_down():
            self.box.on_rotate_begin( self)
            self.dragfunc = self.box.on_rotate
        else:
            self.box.on_scale_begin( self)
            self.dragfunc = self.box.on_scale         

    def on_drag_end(self):
        self.dragging = False
        PigDirector.scene.state.selectOnUp = None
        self.box.surround_node(force=True)
        self.graphicsManager.update_selection_boxes()
        wx.CallAfter(wx.GetApp().selection_refresh)
        self.dragfunc = None
        if self.tick_action:
            self.tick_action.abort()
        Mouse.cursor = Opioid2D.HWCursor.arrow

    def on_drag(self):
        self.dragfunc( self)
        
    def on_release(self):
        PigDirector.scene.state.mouse_locked_by = None
